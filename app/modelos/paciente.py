from datetime import datetime

from app.modelos.constantes import RISCOS
from app.modelos.pessoa import Pessoa
from modelos.constantes import SEM_PREFERENCIA, normalizar_risco

"""
A classe Paciente agora herda de Pessoa
@property simplifica a criação de getters e setters
"""


class Paciente(Pessoa):
    def __init__(self, cpf, nome, idade, tipo_preferencial=SEM_PREFERENCIA, risco="VERDE", sintomas="",
                 id_atendimento=None):
        super().__init__(nome)
        self._cpf = cpf
        self.idade = idade
        self._tipo_preferencial = tipo_preferencial or SEM_PREFERENCIA
        self.risco = risco
        self.sintomas = sintomas
        self.id_atendimento = id_atendimento

    @property
    def cpf(self) -> str:
        return self._cpf

    @property
    def idade(self) -> int:
        return self._idade

    @idade.setter
    def idade(self, valor):
        valor = int(valor)
        if not 0 <= valor <= 150:
            raise ValueError("Idade inválida (use um valor entre 0 e 150).")
        self._idade = valor

    @property
    def risco(self) -> str:
        return self._risco

    @risco.setter
    def risco(self, valor):
        self._risco = normalizar_risco(valor)

    @property
    def tipo_preferencial(self) -> str:
        return self._tipo_preferencial

    def bonus_preferencial(self):
        """0 = tem preferencia no desempate; 1 = sem preferência"""
        return 1

    def chave_prioridade(self, ordem: int) -> tuple:
        return RISCOS[self._risco], self.bonus_preferencial(), ordem

    def __str__(self) -> str:
        return f"{self.nome} (CPF: {self._cpf}), idade: {self._idade} preferencial: {self._tipo_preferencial}"



class PacientePreferencial(Paciente):
    """Idosos (60+), gestantes, PCDs: desempatam dentro da mesma cor."""

    def __init__(self, cpf, nome, idade, motivo="idoso", **kwargs):
        super().__init__(cpf, nome, idade, tipo_preferencial=motivo, **kwargs)

    @property
    def tipo_preferencial(self) -> str:
        return self._tipo_preferencial

    def bonus_preferencial(self) -> int:
        return 0
