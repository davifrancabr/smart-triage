class Pessoa:
    def __init__(self, nome: str):
        self._nome = nome

    @property
    def nome(self):
        return self._nome

