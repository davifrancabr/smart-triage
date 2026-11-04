import os
from pathlib import Path
import mysql.connector
from mysql.connector import Error

from app.modelos.medico import Medico
from app.modelos.paciente import PacientePreferencial, Paciente
from modelos.constantes import SEM_PREFERENCIA

try:
    from dotenv import load_dotenv

    load_dotenv()

except ImportError:
    pass

SCHEMA = Path(__file__).with_name("modelagem.sql")

_ERROS_SEM_PRERMISSAO = (1044, 1142, 1227)



def config_padrao() -> dict:
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", "3306")),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_NAME") or os.environ.get("DB_DATABASE") or "smart_triage",
    }


class RepositorioDB:
    def __init__(self, config: dict | None = None):
        cfg = dict(config or config_padrao())
        nome_banco = cfg.pop("database")
        self._garantir_banco(cfg, nome_banco)
        self.conn = mysql.connector.connect(database=nome_banco, charset="utf8mb4", **cfg)
        self._criar_tabelas()

    @staticmethod
    def _garantir_banco(cfg: dict, nome_banco: str):
        conn = mysql.connector.connect(charset="utf8mb4", **cfg)
        try:

            cur = conn.cursor()
            try:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{nome_banco}` "
                            "DEFAULT CHARACTER SET utf8mb4")
                conn.commit()
            except Error as e:
                if e.errno not in _ERROS_SEM_PRERMISSAO:
                    raise
            finally:
                cur.close()
        finally:
            conn.close()

    def _criar_tabelas(self):
        script = SCHEMA.read_text(encoding="utf8")
        cur = self.conn.cursor()
        try:
            for comando in script.split(";"):
                linhas = [l for l in comando.splitlines() if not l.strip().startswith("--")]
                sql = "\n".join(linhas).strip()
                if sql:
                    cur.execute(sql)
            self.conn.commit()
        finally:
            cur.close()

    def _executar(self, sql, params=()):
        cur = self.conn.cursor(dictionary=True)

        try:
            cur.execute(sql, params)
            self.conn.commit()
            return cur.lastrowid
        except Error:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def _consultar(self, sql: str, params=()) -> list[dict]:
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute(sql, params)
            return cur.fetchall()
        finally:
            cur.close()

    def _atualizar(self, sql: str, params=()) -> int:
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute(sql, params)
            self.conn.commit()
            return cur.rowcount
        except Error:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def fechar(self):
        if self.conn.is_connected():
            self.conn.close()

    # Medicos
    def cadastrar_medico(self, m: Medico):
        self._atualizar("INSERT INTO medicos (crm, nome, especialidade) VALUES (%s, %s, %s)",
                        (m.crm, m.nome, m.especialidade))

    def listar_medicos(self) -> list[Medico]:
        rows = self._consultar("SELECT crm, nome, especialidade FROM medicos ORDER BY nome")
        return [Medico(r["crm"], r["nome"], r["especialidade"]) for r in rows]

    # Pacientes
    def registrar_chegada(self, p: Paciente) -> int:
        cur = self.conn.cursor(dictionary=True)

        try:
            cur.execute("SELECT id_atendimento FROM triagens "
                        "WHERE cpf_paciente = %s AND status IN ('Aguardando', 'Em Atendimento') LIMIT 1", (p.cpf,),
                        )
            if cur.fetchone():
                raise ValueError("Esse paciente já possui uma triagem em andamento")
            cur.execute(
                "INSERT INTO pacientes (cpf, nome, idade, tipo_preferencial) "
                "VALUES (%s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE nome = VALUES(nome), idade = VALUES(idade), "
                "tipo_preferencial = VALUES(tipo_preferencial)",
                (p.cpf, p.nome, p.idade, p.tipo_preferencial),
            )
            cur.execute(
                "INSERT INTO triagens (cpf_paciente, sintomas_relatados, classificacao_risco) "
                "VALUES (%s, %s, %s)",
                (p.cpf, p.sintomas, p.risco.capitalize()),
            )
            p.id_atendimento = cur.lastrowid
            self.conn.commit()
            return p.id_atendimento
        except (Error, ValueError):
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def pacientes_aguardando(self) -> list[Paciente]:
        rows = self._consultar(
            """
            SELECT p.cpf,
                   p.nome,
                   p.idade,
                   p.tipo_preferencial,
                   t.id_atendimento,
                   t.classificacao_risco,
                   t.sintomas_relatados
            FROM triagens t
                     JOIN pacientes p ON p.cpf = t.cpf_paciente
            WHERE t.status = 'Aguardando'
            ORDER BY t.id_atendimento
            """
        )
        return [self._linha_para_paciente(r) for r in rows]

    def cadastrar_paciente(self, p):
        p.id = self._executar("INSERT INTO pacientes (cpf, nome, idade, tipo_preferencial)"
                              "VALUES (%s, %s, %s, %s)",
                              (p.cpf, p.nome, p.idade, p.tipo_preferencial))
        return p.id

    def registrar_atendimento(self, p):
        p.id = self._executar(
            "INSERT INTO triagens (cpf_paciente, crm_medico, observacao, sintomas_relatados, classificacao_risco, status, data_hora_chegada) VALUES (%s, %s ,%s, %s, %s, %s, %s)",
            (p.cpf_paciente, p.crm_medico, p.observacao, p.sintomas_relatados, p.classificacao_risco, p.status,
             p.data_hora_chegada))
        return p.id

    @staticmethod
    def _linha_para_paciente(r: dict) -> Paciente:
        tipo = r["tipo_preferencial"] or SEM_PREFERENCIA
        extras = dict(
            risco=r["classificacao_risco"],
            sintomas=r["sintomas_relatados"],
            id_atendimento=r["id_atendimento"],
        )
        if tipo != SEM_PREFERENCIA:
            return PacientePreferencial(r["cpf"], r["nome"], r["idade"], motivo=tipo, **extras)
        return Paciente(r["cpf"], r["nome"], r["idade"], **extras)

    # Atendimento
    def atualizar_risco(self, id_atendimento: int, novo_risco: str) -> bool:
        existe = self._consultar(
            "SELECT 1 as ok FROM triagens WHERE id_atendimento = %s AND status = 'Aguardando'",
            (id_atendimento,),
        )
        if not existe:
            return False
        self._atualizar(
            "UPDATE triagens SET classificacao_risco = %s WHERE id_atendimento = %s",
            (novo_risco.capitalize(), id_atendimento),
        )
        return True

    def iniciar_atendimento(self, id_atendimento: int, crm_medico: str) -> bool:
        return self._atualizar(
            """
            UPDATE triagens
            SET status     = 'Em Atendimento',
                crm_medico = %s
            WHERE id_atendimento = %s
              AND status = 'Aguardando'
            """,
            (crm_medico, id_atendimento),
        ) > 0

    def finalizar_atendimento(self, id_atendimento: int, observacao: str = "") -> bool:
        return self._atualizar(
            """
            UPDATE triagens
            SET status     = 'Atendido',
                observacao = %s
            WHERE id_atendimento = %s
              AND status = 'Em Atendimento',
            """,
            (observacao or None, id_atendimento),
        ) > 0

    def atender_paciente(self, id_atendimento: int, crm_medico: str, observacao: str = "") -> bool:
        cur = self.conn.cursor()

        try:
            cur.execute("""
                        UPDATE triagens
                        SET status     = 'Em Atendimento',
                            crm_medico = %s
                        WHERE id_atendimento = %s
                          AND status = 'Aguardando'
                        """,
                        (crm_medico, id_atendimento),
                        )
            if cur.rowcount == 0:
                self.conn.rollback()
                return False
            cur.execute("""
                        UPDATE triagens
                        SET status     = 'Atendido',
                            observacao = %s
                        WHERE id_atendimento = %s
                          AND status = 'Em Atendimento'
                        """,
                        (observacao or None, id_atendimento),
                        )
            self.conn.commit()
            return True
        except Error:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def cancelar_triagem(self, id_atendimento: int) -> bool:
        return self._atualizar(
            """
            UPDATE triagens
            SET status = 'Cancelado'
            WHERE id_atendimento = %s
              AND status = 'Aguardando'
            """,
            (id_atendimento,),
        ) > 0

    def historico(self) -> list[dict]:
        return self._consultar(
            """
            SELECT t.id_atendimento,
                   t.data_hora_chegada,
                   p.nome                AS paciente,
                   t.classificacao_risco AS risco,
                   t.status,
                   t.observacao,
                   m.nome                as medico,
                   m.especialidade
            FROM triagens t
                     JOIN pacientes p ON p.cpf = t.cpf_paciente
                     LEFT JOIN medicos m ON m.crm = t.crm_medico
            WHERE t.status <> 'Aguardando'
            ORDER BY t.data_hora_chegada DESC, t.id_atendimento DESC
            """)
