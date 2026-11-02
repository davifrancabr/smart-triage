from app.modelos.pessoa import Pessoa


class Medico(Pessoa):
    def __init__(self, nome, idade, cpf: str, especialidade: str, id_ = None):
        super().__init__(nome, idade, cpf)
        self.__total_atendimentos = 0
        self.especialidade = especialidade
        self.id = id_

    def atender(self, paciente, repo, observacao = ""):
        print(f"Dr(a). {self.nome} está atendendo {paciente.nome}")
        repo.registrar_atendimento(paciente.id)
        self.__total_atendimentos = self.__total_atendimentos + 1

    def get_total_atendimentos(self):
        return self.__total_atendimentos

