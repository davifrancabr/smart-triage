import unittest

import mysql.connector
from mysql.connector import Error, IntegrityError

from app.db.repositorio import RepositorioDB, config_padrao
from app.modelos.medico import Medico
from app.modelos.paciente import Paciente, PacientePreferencial

BANCO_TESTE = "smart_triage_test"


class TestRepositorio(unittest.TestCase):
    def setUp(self):
        cfg = config_padrao()
        cfg["database"] = BANCO_TESTE
        self.cfg = cfg
        try:
            admin = {k: v for k, v in cfg.items() if k != "database"}
            conn = mysql.connector.connect(**admin)
            cur = conn.cursor()
            cur.execute(f"DROP DATABASE IF EXISTS `{BANCO_TESTE}`")
            cur.execute(f"CREATE DATABASE `{BANCO_TESTE}` CHARACTER SET utf8mb4")
            conn.commit()
            conn.close()
            self.repo = RepositorioDB(cfg)
        except Error as e:
            self.skipTest(f"MySQL indisponível para testes de integração: {e}")
        self.addCleanup(self.repo.fechar)

    def paciente(self, n, risco="VERDE", pref=None, sintomas="dor"):
        extras = dict(risco=risco, sintomas=sintomas)
        cpf = f"{n:011d}"
        if pref:
            return PacientePreferencial(cpf, f"Pac{n}", 30, motivo=pref, **extras)
        return Paciente(cpf, f"Pac{n}", 30, **extras)

    def test_chegada_e_fila(self):
        a = self.paciente(1, "VERMELHO", sintomas="dor no peito")
        b = self.paciente(2, "VERDE", pref="idoso")
        self.repo.registrar_chegada(a)
        self.repo.registrar_chegada(b)
        self.assertIsNotNone(a.id_atendimento)
        fila = self.repo.pacientes_aguardando()
        self.assertEqual([p.nome for p in fila], ["Pac1", "Pac2"])  # ordem de chegada
        self.assertEqual(fila[0].risco, "VERMELHO")
        self.assertEqual(fila[0].sintomas, "dor no peito")
        self.assertIsInstance(fila[1], PacientePreferencial)
        self.assertEqual(fila[1].tipo_preferencial, "idoso")
        self.assertNotIsInstance(fila[0], PacientePreferencial)

    def test_triagem_duplicada_e_recusada(self):
        self.repo.registrar_chegada(self.paciente(1))
        with self.assertRaises(ValueError):
            self.repo.registrar_chegada(self.paciente(1))
        self.assertEqual(len(self.repo.pacientes_aguardando()), 1)

    def test_paciente_pode_voltar_depois_de_atendido(self):
        self.repo.cadastrar_medico(Medico("1", "Ana", "Clínico"))
        p = self.paciente(1)
        self.repo.registrar_chegada(p)
        self.assertTrue(self.repo.atender_paciente(p.id_atendimento, "1", "ok"))
        self.repo.registrar_chegada(self.paciente(1, "AMARELO"))
        self.assertEqual(len(self.repo.pacientes_aguardando()), 1)

    def test_atendimento_e_historico(self):
        self.repo.cadastrar_medico(Medico("1", "Ana", "Clínico"))
        p = self.paciente(1, "AMARELO")
        self.repo.registrar_chegada(p)
        self.assertTrue(self.repo.atender_paciente(p.id_atendimento, "1", "paciente estável"))
        self.assertEqual(self.repo.pacientes_aguardando(), [])
        h = self.repo.historico()
        self.assertEqual(len(h), 1)
        self.assertEqual(h[0]["paciente"], "Pac1")
        self.assertEqual(h[0]["medico"], "Ana")
        self.assertEqual(h[0]["risco"], "Amarelo")
        self.assertEqual(h[0]["status"], "Atendido")
        self.assertEqual(h[0]["observacao"], "paciente estável")

    def test_nao_atende_duas_vezes(self):
        self.repo.cadastrar_medico(Medico("1", "Ana", "Clínico"))
        p = self.paciente(1)
        self.repo.registrar_chegada(p)
        self.assertTrue(self.repo.atender_paciente(p.id_atendimento, "1"))
        self.assertFalse(self.repo.atender_paciente(p.id_atendimento, "1"))

    def test_atender_com_medico_inexistente_faz_rollback(self):
        p = self.paciente(1)
        self.repo.registrar_chegada(p)
        with self.assertRaises(IntegrityError):
            self.repo.atender_paciente(p.id_atendimento, "999", "x")
        self.assertEqual(len(self.repo.pacientes_aguardando()), 1)  # continua aguardando

    def test_ciclo_iniciar_finalizar(self):
        self.repo.cadastrar_medico(Medico("1", "Ana", "Clínico"))
        p = self.paciente(1)
        self.repo.registrar_chegada(p)
        self.assertFalse(self.repo.finalizar_atendimento(p.id_atendimento))  # ainda não iniciou
        self.assertTrue(self.repo.iniciar_atendimento(p.id_atendimento, "1"))
        self.assertEqual(self.repo.historico()[0]["status"], "Em Atendimento")
        self.assertTrue(self.repo.finalizar_atendimento(p.id_atendimento, "feito"))
        self.assertEqual(self.repo.historico()[0]["status"], "Atendido")

    def test_atualizar_risco(self):
        p = self.paciente(1, "VERDE")
        self.repo.registrar_chegada(p)
        self.assertTrue(self.repo.atualizar_risco(p.id_atendimento, "VERMELHO"))
        self.assertEqual(self.repo.pacientes_aguardando()[0].risco, "VERMELHO")
        self.assertFalse(self.repo.atualizar_risco(999, "VERMELHO"))

    def test_cancelar(self):
        p = self.paciente(1)
        self.repo.registrar_chegada(p)
        self.assertTrue(self.repo.cancelar_triagem(p.id_atendimento))
        self.assertEqual(self.repo.pacientes_aguardando(), [])

    def test_medicos(self):
        self.repo.cadastrar_medico(Medico("2", "Bia", "Cardio"))
        self.repo.cadastrar_medico(Medico("1", "Ana", "Clínico"))
        self.assertEqual([m.crm for m in self.repo.listar_medicos()], ["1", "2"])  # por nome
        with self.assertRaises(IntegrityError):
            self.repo.cadastrar_medico(Medico("1", "Outra", "X"))

    def test_acentos_sobrevivem(self):
        p = self.paciente(1, sintomas="dor de cabeça e náusea")
        self.repo.registrar_chegada(p)
        self.assertEqual(self.repo.pacientes_aguardando()[0].sintomas, "dor de cabeça e náusea")


if __name__ == "__main__":
    unittest.main()
