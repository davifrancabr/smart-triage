from app.modelos.pessoa import Pessoa


class Paciente(Pessoa):
    def __init__(self, nome, idade, sintomas, id):
        super().__init__(nome, idade)
        self._idade = int(idade)
        self._sintomas = sintomas
        self.id = id_

    @property
    def idade(self):
        return self._idade

    @property
    def sintomas(self):
        return self._sintomas

    def mostrar(self):
        print(f"Nome: {self.nome}, idade: {self._idade}, sintomas: {self._sintomas}")

    def get_idade(self):
        return self._idade

    def set_idade(self, nova_idade):
        if nova_idade >= 0:
           self._idade = nova_idade
        else:
            print("Idade inválida")

class PacientePreferencial(Paciente):
    def __init__(self, nome, idade, sintoma, motivo):
        super().__init__(nome, idade, sintoma)
        self.motivo = motivo

    def mostrar(self):
        super().mostrar()
        print(f"Atendimento preferencial. Motivo: {self.motivo}")
