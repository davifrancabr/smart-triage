import itertools

from app.estruturas.fila_prioridade import FilaPrioridade
from app.modelos.paciente import PacientePreferencial, Paciente


class Triagem:
    def __init__(self, repo, classificador):
        self.repo = repo
        self.ia = classificador
        self.fila = FilaPrioridade()
        self.__contador = itertools.count()
        self.recarregar_fila()

    def recarregar_fila(self):
        self.fila = FilaPrioridade()
        self.__contador = itertools.count()
        for p in self.repo.pacientes_aguardando():
            self.fila.inserir(p.chave_prioridade(next(self.__contador)), p)


    def adicionar(self, nome, idade, cpf, sintomas, preferencial_motivo = None):
        risco, just, origem = self.ia.analisar_sintomas( sintomas)
        if preferencial_motivo:
            p = PacientePreferencial(nome, idade, cpf, sintomas, risco, motivo=preferencial_motivo)
        else:
            p = Paciente(nome, idade, cpf, sintomas, risco)
        self.repo.inserir_paciente(p)
        self.fila.inserir(p.chave_prioridade(next(self.__contador)), p)
        return p, just, origem

    def chamar_proximo(self, medico, obervacao = ""):
        if self.fila.vazia():
            return None
        paciente = self.fila.remover()
        medico.atender(paciente, obervacao)
        return paciente

    def corrigir_risco(self, paciente_id, novo_risco):
        self.repo.atualizar_risco(paciente_id, novo_risco)
        self.recarregar_fila()


