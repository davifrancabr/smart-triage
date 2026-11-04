import itertools
import re

from app.estruturas.fila_prioridade import FilaPrioridade
from app.modelos.paciente import PacientePreferencial, Paciente
from modelos.constantes import normalizar_risco


class Triagem:
    def __init__(self, repo, classificador):
        self.repo = repo
        self.ia = classificador
        self.fila = FilaPrioridade()
        self._contador = itertools.count()
        self.recarregar_fila()

    def recarregar_fila(self):
        self.fila = FilaPrioridade()
        self._contador = itertools.count()
        for p in self.repo.pacientes_aguardando():
            self._enfileirar(p)

    def _enfileirar(self, paciente: Paciente):
        self.fila.inserir(paciente.chave_prioridade(next(self._contador)), paciente)

    def adicionar(self, nome, idade, cpf, sintomas, preferencial_motivo=None):
        cpf = re.sub(r"\D", "", cpf or "")
        if len(cpf) != 11:
            raise ValueError("CPF Inválido: informe 11 dígitos.")
        if not (sintomas or "").strip():
            raise ValueError("Informe os sintomas do paciente.")

        resultado = self.ia.analisar_sintomas(sintomas)
        risco = normalizar_risco(resultado["risco"])
        dados = dict(risco=risco, sintomas=sintomas.strip())

        if preferencial_motivo:
            paciente = PacientePreferencial(cpf, nome, idade, motivo=preferencial_motivo, **dados)
        else:
            paciente = Paciente(cpf, nome, idade, **dados)

        self.repo.registrar_chegada(paciente)
        self._enfileirar(paciente)
        return paciente, resultado.get("justificativa", ""), resultado.get("origem", "IA")

    def chamar_proximo(self, medico, obervacao=""):
        paciente = self.fila.espiar()
        if paciente is None:
            return None
        if not medico.atender(paciente, self.repo, obervacao):
            self.recarregar_fila()
            return None
        self.fila.remover()
        return paciente

    def corrigir_risco(self, id_atendimento: int, novo_risco: str):
        novo_risco = normalizar_risco(novo_risco)
        if not self.repo.atualizar_risco(id_atendimento, novo_risco):
            raise ValueError("Paciente não encontrado na fila de espera.")
        self.recarregar_fila()
