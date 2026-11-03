import os
from pathlib import Path

import mysql.connector
from mysql.connector import Error, IntegrityError

from db.connection import conectar

SCHEMA = Path(__file__).with_name("modelagem.sql")

def config_padrao():
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", "3306")),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_DATABASE", "triage_smart"),
    }

class RepositorioDB:
    def __init__(self, config = None):
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
        p.id = self._executar("INSERT INTO pacientes (cpf, nome, tipo_preferencial)"
                              "VALUES (%s, %s, %s)",
                              (p.cpf, p.nome, p.tipo_preferencial))
        return p.id
        #conexao = conectar()
        #if not conexao:
        #    print("Erro ao conectar no banco")
        #    return False

        #try:
        #    cursor = conexao.cursor()

        #    # Insere na tabela pacientes
        #    sql_paciente = """
        #                   INSERT INTO paciente (cpf, nome, tipo_preferencial)
        #                   VALUES (%s, %s, %s) \
        #                   """
        #    cursor.execute(sql_paciente, (cpf, nome, tipo_preferencial))

        #    # Insere na tabela triagens
        #    sql_triagem = """
        #                  INSERT INTO triagem
        #                      (cpf_paciente, sintomas_relatados, classificacao_risco, status)
        #                  VALUES (%s, %s, %s, 'Aguardando') \
        #                  """
        #    cursor.execute(sql_triagem, (cpf, sintomas, classificacao_risco))

        #    conexao.commit()
        #    print("Paciente cadastrado com sucesso!")
        #    return True

        #except Exception as erro:
        #    print(f"Erro ao cadastrar paciente: {erro}")
        #    conexao.rollback()
        #    return False

        #finally:
        #    if conexao.is_connected():
        #        cursor.close()
        #        conexao.close()
    def cadastrar_medico(self, p):
        p.id = self._executar(
            "INSERT INTO medico (crm, nome)"
            "VALUES (%s, %s)",
            (p.crm, p.nome)
        )
        return p.id
        conexao = conectar()
        if not conexao:
            print("Erro ao conectar no banco")
            return False

        try:
            cursor = conexao.cursor()

            sql = """
                  INSERT INTO medico (crm, nome)
                  VALUES (%s, %s) \
                  """
            cursor.execute(sql, (crm, nome))
            conexao.commit()

            print("Médico cadastrado com sucesso!")
            return True

        except Exception as erro:
            print(f"Erro ao cadastrar médico: {erro}")
            conexao.rollback()
            return False

        finally:
            if conexao.is_connected():
                cursor.close()
                conexao.close()

    def listar_fila(self):
        resultado =  self._executar("""
            SELECT 
                t.id_atendimento,
                p.nome AS Nome_Paciente,
                p.tipo_preferencial,
                t.sintomas_relatados,
                t.classificacao_risco,
                t.data_hora_chegada
            FROM triagem t
            JOIN paciente p ON t.cpf_paciente = p.cpf
            WHERE t.status = 'Aguardando'
            ORDER BY 
                CASE t.classificacao_risco
                    WHEN 'Vermelho' THEN 1
                    WHEN 'Amarelo' THEN 2
                    WHEN 'Verde' THEN 3
                    ELSE 4
                END ASC,
                CASE 
                    WHEN p.tipo_preferencial IS NOT NULL THEN 0 
                    ELSE 1 
                END ASC,
                t.data_hora_chegada ASC
        """)
        return resultado

    def atender_paciente(self, id_atendimento, crm_medico):
        resultado = self._executar("""
            UPDATE triagem
            SET status = 'Em Atendimento',
                crm_medico = %s
            WHERE id_atendimento = %s
              AND status = 'Aguardando'
        """, (crm_medico, id_atendimento))

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
