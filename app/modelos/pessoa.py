class Pessoa:
    def __init__(self, nome: str):
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("O nome não pode ser vazio.")
        self._nome = nome

    @property
    def nome(self) -> str:
        return self._nome

