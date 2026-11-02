class Paciente:
    def __init__(self, nome, idade, sintomas):
        self.nome = nome
        self.__idade = idade
        self.sintomas = sintomas

    def mostrar(self):
        print(f"Nome: {self.nome}, idade: {self.__idade}, sintomas: {self.sintomas}")

    def get_idade(self):
        return self.__idade

    def set_idade(self, nova_idade):
        if nova_idade >= 0:
           self.__idade = nova_idade
        else:
            print("idade inválida")

class PacientePreferencial(Paciente):
    def __init__(self, nome, idade, sintoma, motivo):
        super().__init__(nome, idade, sintoma)
        self.motivo = motivo

    def mostrar(self):
        super().mostrar()
        print(f"Atendimento preferencial. Motivo: {self.motivo}")
