from datetime import datetime

from app.modelos.constantes import RISCOS
from app.modelos.pessoa import Pessoa

"""
A classe Paciente agora herda de Pessoa
@property simplifica a criação de getters e setters
"""
class Paciente(Pessoa):
    def __init__(self, nome: str, idade, cpf: str, sintomas: str, risco = "Verde", id_ = None, chegada = None):
        super().__init__(nome, cpf)
        self._idade = int(idade)
        self._sintomas = sintomas
        self._cpf = cpf
        self._risco = risco
        self.id = id_
        self.chegada = chegada or datetime.now().isoformat(timespec='seconds')

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
    def sintomas(self):
        return self._sintomas

    @property
    def risco(self):
        return self._risco

    @risco.setter
    def risco(self, valor):
        valor = valor.upper()
        if valor not in RISCOS:
            raise ValueError(f"Risco inválido: {valor}")
        self._risco = valor

    @property
    def tipo(self):
        return "NORMAL"

    def bonus_preferencial(self):
        """0 = tem preferencia no desempate; 1 = sem preferência"""
        return 1

    def chave_prioridade(self, ordem):
        return RISCOS[self._risco], self.bonus_preferencial(), ordem


    def __str__(self):
        print(f"Nome: {self.nome}(CPF: {self._cpf}), idade: {self._idade}, sintomas: {self._sintomas}")


class PacientePreferencial(Paciente):
    """Idosos (60+), gestantes, PCDs: desempatam dentro da mesma cor."""

    def __init__(self, *args, motivo="idoso", **kwargs):
        super().__init__(*args, **kwargs)
        self.motivo = motivo

    @property
    def tipo(self):
        return f"PREFERENCIAL({self.motivo})"

    def bonus_preferencial(self):
        return 0

    def mostrar(self):
        super().mostrar()
        print(f"Atendimento preferencial. Motivo: {self.motivo}")
