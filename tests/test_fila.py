import unittest

from app.estruturas.fila_prioridade import FilaPrioridade


class TestFilaPrioridade(unittest.TestCase):
    def test_ordem_por_chave(self):
        f = FilaPrioridade()
        for chave, item in [(3, "c"), (1, "a"), (2, "b"), (0, "z")]:
            f.inserir(chave, item)
        self.assertEqual([f.remover() for _ in range(4)], ["z", "a", "b", "c"])

    def test_fila_vazia(self):
        f = FilaPrioridade()
        self.assertTrue(f.vazia())
        self.assertIsNone(f.espiar())
        with self.assertRaises(IndexError):
            f.remover()

    def test_ordenada_nao_consome(self):
        f = FilaPrioridade()
        f.inserir(2, "b")
        f.inserir(1, "a")
        self.assertEqual(f.ordenada(), ["a", "b"])
        self.assertEqual(len(f), 2)

    def test_chaves_em_tupla_desempatam_por_ordem(self):
        f = FilaPrioridade()
        f.inserir((0, 1, 0), "primeiro")
        f.inserir((0, 1, 1), "segundo")
        f.inserir((0, 0, 2), "preferencial")
        self.assertEqual(f.ordenada(), ["preferencial", "primeiro", "segundo"])


if __name__ == "__main__":
    unittest.main()
