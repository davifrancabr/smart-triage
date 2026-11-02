class Medico:
    def __init__(self, nome):
        self.nome = nome
        self.__total_atendimentos = 0

    def atender(self, paciente):
        print(f"Dr(a). {self.nome} está atendendo {paciente.nome}")
        self.__total_atendimentos = self.__total_atendimentos + 1

    def get_total_atendimentos(self):
        return self.__total_atendimentos

