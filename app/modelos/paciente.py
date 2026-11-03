from datetime import datetime

from app.modelos.constantes import RISCOS
from app.modelos.pessoa import Pessoa

"""
A classe Paciente agora herda de Pessoa
@property simplifica a criação de getters e setters
"""


class Paciente(Pessoa):
    def __init__(self, cpf: str, nome: str, idade, tipo_preferencial: str, risco:str, sintomas: str, id_=None):
        super().__init__(nome)
        self._idade = int(idade)
        self._cpf = cpf
        self._risco = risco
        self._sintomas = sintomas
        self._tipo_preferencial = tipo_preferencial
        self.id = id_

    @property
    def idade(self):
        return self._idade

    @idade.setter
    def idade(self, nova_idade):
        if nova_idade >= 0:
            self._idade = nova_idade
        else:
            print("Idade inválida")

    @property
    def tipo_preferencial(self):
        return self._tipo_preferencial

    def bonus_preferencial(self):
        """0 = tem preferencia no desempate; 1 = sem preferência"""
        return 1

    def chave_prioridade(self, ordem):
        return RISCOS[self._risco], self.bonus_preferencial(), ordem

    def __str__(self):
        return f"Nome: {self.nome}(CPF: {self._cpf}), idade: {self._idade}, tipo preferêncial: {self._tipo_preferencial}"

class PacientePreferencial(Paciente):
    """Idosos (60+), gestantes, PCDs: desempatam dentro da mesma cor."""

    def __init__(self, *args, motivo="idoso", **kwargs):
        super().__init__(*args, **kwargs)
        self.motivo = motivo

    @property
    def tipo_preferencial(self):
        return f"PREFERENCIAL({self.motivo})"

    def bonus_preferencial(self):
        return 0
