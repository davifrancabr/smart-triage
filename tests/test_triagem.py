import unittest

import mysql.connector

from db.repositorio import config_padrao, RepositorioDB
from ia.ClassificadorIAService import ClassificadorIA
from servicos.triagem import Triagem


class ClassficadorFalso:
    def classificar(self, sintomas):
        return ClassificadorIA.analisar_sintomas(sintomas)


BANCO_TESTE = "smart_triage_test"


def recriar_banco_teste():
    cfg = config_padrao()
    cfg.pop("database")
    conn = mysql.connector.connect(**cfg)
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS `{BANCO_TESTE}`")
    conn.commit()
    cur.close()
    conn.close()


class TestTriagem(unittest.TestCase):
    def setUp(self):
        try:
            recriar_banco_teste()
            self.repo = RepositorioDB({"database": BANCO_TESTE})
        except mysql.connector.Error as e:
            if e.errno in (2002, 2003, 1045):
                self.skipTest(self.repo, ClassficadorFalso())
            raise
        self.triagem = Triagem(self.repo, ClassficadorFalso())

    def tearDown(self):
        if hasattr(self, "repo"):
            self.repo.fechar()

    def test_gravidade_vence_chegada(self):
        ...
