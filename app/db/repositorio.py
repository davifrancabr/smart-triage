import os
from pathlib import Path

import mysql.connector
from mysql.connector import Error, IntegrityError

from db.connection import conectar
from modelos.medico import Medico
from modelos.paciente import PacientePreferencial, Paciente

SCHEMA = Path(__file__).with_name("modelagem.sql")

"""
_executar -> insert/update/delete
_consultar -> read only
"""


def config_padrao():
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", "3306")),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_DATABASE", "triage_smart"),
    }


class RepositorioDB:
    def __init__(self, config=None):
        cfg = {**config_padrao(), **(config or {})}
        nome_banco = cfg.pop("database")
        self._garantir_banco(cfg, nome_banco)
        self.conn = mysql.connector.connect(database=nome_banco, chartset="utf8mb4", **cfg)
        self._criar_tabelas()

    @staticmethod
    def _garantir_banco(self, cfg, nome_banco):
        conn = mysql.connector.connect(**cfg)
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{nome_banco}` "
                    "DEFAULT CHARACTER SET utf8mb4")
        conn.commit()
        cur.close()
        conn.close()

    def _criar_tabelas(self):
        cur = self.conn.cursor()
        for comando in SCHEMA.read_text(encoding="utf8").split(";"):
            linhas = [l for l in comando.splitlines() if not l.strip().startswith("--")]
            sql = "\n".join(linhas).strip()
            if sql:
                cur.execute(sql)
        self.conn.commit()
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

    def _consultar(self, sql, params=()):
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute(sql, params)
        finally:
            cur.close()

    # Definir dados: apenas cpf, nome e tipo preferencial?
    def cadastrar_paciente(self, p):
        p.id = self._executar("INSERT INTO pacientes (cpf, nome, idade, tipo_preferencial)"
                              "VALUES (%s, %s, %s, %s)",
                              (p.cpf, p.nome, p.idade, p.tipo_preferencial))
        return p.id

    def cadastrar_medico(self, m):
        m.id = self._executar(
            "INSERT INTO medico (crm, nome, especialidade)"
            "VALUES (%s, %s, %s)",
            (m.crm, m.nome, m.especialidade)
        )
        return m.id

    def registrar_atendimento(self, p):
        p.id = self._executar(
            "INSERT INTO triagens (cpf_paciente, crm_medico, observacao, sintomas_relatados, classificacao_risco, status, data_hora_chegada) VALUES (%s, %s ,%s, %s, %s, %s, %s)",
            (p.cpf_paciente, p.crm_medico, p.observacao, p.sintomas_relatados, p.classificacao_risco, p.status,
             p.data_hora_chegada))
        return p.id

    @staticmethod
    def _linha_para_paciente(r):
        args = (r["nome"], r["idade"], r["tipo_preferencial"])
        if r["tipo_preferencial"] != "Normal":
            return PacientePreferencial(*args, motivo=r["tipo_preferencial"])
        return Paciente(*args)

    def pacientes_aguardando(self):
        rows = self._consultar(
            "SELECT * FROM triagens WHERE status = 'Aguardando' ORDER BY id_atendimento")
        return [self._linha_para_paciente(r) for r in rows]

    def listar_medicos(self):
        rows = self._consultar("SELECT * FROM medicos ORDER BY crm")
        return [Medico(r["nome"], r["especialidade"]) for r in rows]

    def historico(self):
        return self._consultar("""
                               SELECT a.id_atendimento,
                                      a.data_hora_chegada,
                                      p.nome AS paciente,
                                      p.risco,
                                      m.nome AS medico,
                                      m.especialidade,
                                      a.observacao,
                                      a.sintomas_relatados,
                                      a.classificacao_risco,
                                      a.status
                               FROM triagens a
                                        JOIN pacientes p ON p.cpf = a.cpf_paciente
                                        JOIN medicos m ON m.crm = a.crm_medico
                               ORDER BY a.cpf DESC""")

    def atualizar_status_paciente(self, p):
        self._executar("UPDATE triagens SET status=%s WHERE id_atendimento=%s", (p.status, p.id_atendimento))

    def atualizar_risco(self, p):
        ...

    def remover_paciente(self):
        ...

    def fechar(self):
        self.conn.close()

    def finalizar_atendimento(self, id_atendimento):
        conexao = conectar()
        if not conexao:
            print("Erro ao conectar no banco")
            return False

        try:
            cursor = conexao.cursor()

            sql = """
                  UPDATE triagem
                  SET status = 'Atendido'
                  WHERE id_atendimento = %s
                    AND status = 'Em Atendimento' \
                  """
            cursor.execute(sql, (id_atendimento,))
            conexao.commit()

            if cursor.rowcount > 0:
                print("Atendimento finalizado!")
                return True
            else:
                print("Atendimento não encontrado ou não estava em andamento.")
                return False

        except Exception as erro:
            print(f"Erro ao finalizar: {erro}")
            conexao.rollback()
            return False

        finally:
            if conexao.is_connected():
                cursor.close()
                conexao.close()
