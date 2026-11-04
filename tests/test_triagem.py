import unittest

from app.modelos.medico import Medico
from app.modelos.paciente import Paciente, PacientePreferencial
from app.servicos.triagem import Triagem
from tests.fakes import ClassificadorFalso, RepoFalso


def cpf(n: int) -> str:
    return f"{n:011d}"


class TestTriagem(unittest.TestCase):
    def setUp(self):
        self.repo = RepoFalso()
        self.ia = ClassificadorFalso({
            "grave": "VERMELHO", "medio": "AMARELO", "leve": "VERDE",
        })
        self.triagem = Triagem(self.repo, self.ia)
        self.medico = Medico("123", "Ana", "Clínico")

    def nomes_na_fila(self):
        return [p.nome for p in self.triagem.fila.ordenada()]

    def test_gravidade_vence_chegada(self):
        self.triagem.adicionar("Leve", 30, cpf(1), "leve")
        self.triagem.adicionar("Medio", 30, cpf(2), "medio")
        self.triagem.adicionar("Grave", 30, cpf(3), "grave")
        self.assertEqual(self.nomes_na_fila(), ["Grave", "Medio", "Leve"])

    def test_preferencial_desempata_mesma_gravidade(self):
        self.triagem.adicionar("Normal", 30, cpf(1), "leve")
        self.triagem.adicionar("Idoso", 80, cpf(2), "leve", preferencial_motivo="idoso")
        self.assertEqual(self.nomes_na_fila(), ["Idoso", "Normal"])

    def test_gravidade_vence_preferencial(self):
        self.triagem.adicionar("Idoso", 80, cpf(1), "leve", preferencial_motivo="idoso")
        self.triagem.adicionar("Grave", 20, cpf(2), "grave")
        self.assertEqual(self.nomes_na_fila(), ["Grave", "Idoso"])

    def test_chegada_desempata_resto(self):
        self.triagem.adicionar("Primeiro", 30, cpf(1), "leve")
        self.triagem.adicionar("Segundo", 30, cpf(2), "leve")
        self.assertEqual(self.nomes_na_fila(), ["Primeiro", "Segundo"])

    def test_chamar_proximo_atende_e_remove(self):
        self.triagem.adicionar("Leve", 30, cpf(1), "leve")
        self.triagem.adicionar("Grave", 30, cpf(2), "grave")
        atendido = self.triagem.chamar_proximo(self.medico, "ok")
        self.assertEqual(atendido.nome, "Grave")
        self.assertEqual(self.repo.status_de(atendido.id_atendimento), "Atendido")
        self.assertEqual(self.nomes_na_fila(), ["Leve"])

    def test_chamar_proximo_fila_vazia(self):
        self.assertIsNone(self.triagem.chamar_proximo(self.medico))

    def test_paciente_nao_se_perde_se_gravacao_falhar(self):
        self.triagem.adicionar("Grave", 30, cpf(1), "grave")
        self.repo.falhar_ao_atender = True
        self.assertIsNone(self.triagem.chamar_proximo(self.medico))
        self.assertEqual(self.nomes_na_fila(), ["Grave"])

    def test_corrigir_risco_reordena(self):
        self.triagem.adicionar("A", 30, cpf(1), "leve")
        p, _, _ = self.triagem.adicionar("B", 30, cpf(2), "leve")
        self.triagem.corrigir_risco(p.id_atendimento, "Vermelho")
        self.assertEqual(self.nomes_na_fila(), ["B", "A"])

    def test_corrigir_risco_inexistente(self):
        with self.assertRaises(ValueError):
            self.triagem.corrigir_risco(999, "Vermelho")

    def test_corrigir_risco_invalido(self):
        p, _, _ = self.triagem.adicionar("A", 30, cpf(1), "leve")
        with self.assertRaises(ValueError):
            self.triagem.corrigir_risco(p.id_atendimento, "Roxo")

    def test_recarregar_fila_preserva_ordem(self):
        self.triagem.adicionar("Primeiro", 30, cpf(1), "leve")
        self.triagem.adicionar("Segundo", 30, cpf(2), "leve")
        self.triagem.recarregar_fila()
        self.assertEqual(self.nomes_na_fila(), ["Primeiro", "Segundo"])

    def test_paciente_duplicado_na_fila(self):
        self.triagem.adicionar("A", 30, cpf(1), "leve")
        with self.assertRaises(ValueError):
            self.triagem.adicionar("A", 30, cpf(1), "grave")
        self.assertEqual(len(self.triagem.fila), 1)

    def test_validacoes(self):
        with self.assertRaises(ValueError):
            self.triagem.adicionar("A", 30, "123", "leve")  # CPF curto
        with self.assertRaises(ValueError):
            self.triagem.adicionar("A", -1, cpf(1), "leve")  # idade negativa
        with self.assertRaises(ValueError):
            self.triagem.adicionar("", 30, cpf(1), "leve")  # nome vazio
        with self.assertRaises(ValueError):
            self.triagem.adicionar("A", 30, cpf(1), "   ")  # sem sintomas
        self.assertTrue(self.triagem.fila.vazia())

    def test_cpf_com_pontuacao_e_aceito(self):
        p, _, _ = self.triagem.adicionar("A", 30, "000.000.000-01", "leve")
        self.assertEqual(p.cpf, "00000000001")


class TestModelos(unittest.TestCase):
    def test_str_retorna_texto(self):
        p = Paciente("00000000001", "Maria", 40)
        self.assertIsInstance(str(p), str)
        self.assertIn("Maria", str(p))

    def test_risco_e_normalizado(self):
        self.assertEqual(Paciente("1", "A", 1, risco="vermelho").risco, "VERMELHO")

    def test_preferencial_tem_bonus(self):
        normal = Paciente("1", "A", 30)
        pref = PacientePreferencial("2", "B", 70, motivo="idoso")
        self.assertLess(pref.chave_prioridade(5), normal.chave_prioridade(0))


if __name__ == "__main__":
    unittest.main()
