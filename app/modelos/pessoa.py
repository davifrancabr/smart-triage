class Pessoa:
    def __init__(self, nome: str, idade: int, cpf: str):
        self._nome = nome
        self._idade = idade
        self._cpf = cpf

    @property
    def nome(self):
        return self._nome

    @property
    def idade(self):
        return self._idade

    @property
    def cpf(self):
        return self._cpf