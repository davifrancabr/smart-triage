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

    def adicionar(self, nome, idade, cpf, sintomas, preferencial_motivo=None):
        [risco, just, origem] = self.ia.analisar_sintomas(sintomas)
        if preferencial_motivo:
            p = PacientePreferencial(cpf, nome, idade, tipo_preferencial=preferencial_motivo,
                                     motivo=preferencial_motivo)
        else:
            p = Paciente(cpf, nome, idade, tipo_preferencial=preferencial_motivo, risco=risco, sintomas=sintomas)
        self.repo.cadastrar_paciente(p)
        self.fila.inserir(p.chave_prioridade(next(self.__contador)), p)
        return p, just, origem

    def chamar_proximo(self, medico, obervacao=""):
        if self.fila.vazia():
            return None
        paciente = self.fila.remover()
        medico.atender(paciente, self.repo, obervacao)
        return paciente

    def corrigir_risco(self, p):
        self.repo.atualizar_risco(self, p)
        self.recarregar_fila()
