import os
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error, IntegrityError

from app.modelos.medico import Medico
from app.modelos.paciente import PacientePreferencial, Paciente

load_dotenv()

SCHEMA = Path(__file__).with_name("modelagem.sql")

"""
_executar -> insert/update/delete
_consultar -> read only
"""


def config_padrao():
    return {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_DATABASE")
    }


class RepositorioDB:
    def __init__(self, config=None):
        cfg = {**config_padrao(), **(config or {})}
        nome_banco = cfg.pop("database")
        cfg["database"] = nome_banco
        cfg["charset"] = "utf8mb4"
        self._garantir_banco(cfg, nome_banco)
        self.conn = mysql.connector.connect(**cfg)
        self._criar_tabelas()

    @staticmethod
    def _garantir_banco(cfg, nome_banco):
        conn = mysql.connector.connect(**cfg)
        cur = conn.cursor()
        try:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{nome_banco}` "
                        "DEFAULT CHARACTER SET utf8mb4")
            conn.commit()
        finally:
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
            return cur.fetchall()
        finally:
            cur.close()

    def cadastrar_paciente(self, p):
        p.id = self._executar("INSERT INTO pacientes (cpf, nome, idade, tipo_preferencial)"
                              "VALUES (%s, %s, %s, %s)",
                              (p.cpf, p.nome, p.idade, p.tipo_preferencial))
        return p.id

    def cadastrar_medico(self, m):
        m.id = self._executar(
            "INSERT INTO medicos (crm, nome, especialidade)"
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
        args = (r["cpf"], r["nome"], r["idade"], r["tipo_preferencial"])
        if r["tipo_preferencial"]:
            return PacientePreferencial(*args, motivo=r["tipo_preferencial"])
        return Paciente(*args)

    def pacientes_aguardando(self):
        rows = self._consultar("""
                               SELECT p.cpf,
                                      p.nome,
                                      p.idade,
                                      p.tipo_preferencial,
                                      t.id_atendimento,
                                      t.classificacao_risco,
                                      t.sintomas_relatados
                               FROM triagens t
                                        JOIN pacientes p ON p.cpf = t.id_atendimento
                               WHERE t.status = 'Aguardando'
                               ORDER BY t.id_atendimento
                               """)
        return [self._linha_para_paciente(r) for r in rows]

    def listar_medicos(self):
        rows = self._consultar("SELECT * FROM medicos ORDER BY crm")
        return [Medico(r["crm"], r["nome"], r["especialidade"]) for r in rows]

    def historico(self):
        return self._consultar("""
                               SELECT a.id_atendimento,
                                      a.data_hora_chegada,
                                      p.nome AS paciente,
                                      p.classificacao_risco,
                                      m.nome AS medico,
                                      m.especialidade,
                                      a.observacao,
                                      a.sintomas_relatados,
                                      a.classificacao_risco,
                                      a.status
                               FROM triagens a
                                        JOIN pacientes p ON p.cpf = a.cpf_paciente
                                        LEFT JOIN medicos m ON m.crm = a.crm_medico
                               ORDER BY a.data_hora_chegada DESC""")

    def atualizar_status_paciente(self, p):
        self._executar("UPDATE triagens SET status=%s WHERE id_atendimento=%s", (p.status, p.id_atendimento))

    def atualizar_risco(self, p):
        ...

    def remover_paciente(self):
        ...

    def fechar(self):
        self.conn.close()
