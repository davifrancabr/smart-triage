from app.modelos.pessoa import Pessoa


class Medico(Pessoa):
    def __init__(self, nome, cpf: str, crm:str , especialidade: str, id_ = None):
        super().__init__(nome,  cpf)
        self.especialidade = especialidade
        self._crm = crm
        self._nome = nome
        self.id = id_

    @property
    def crm(self):
        return self._crm

    @property
    def nome(self):
        return self._nome

    def atender(self, paciente, repo, observacao = ""):
        print(f"Dr(a). {self.nome} está atendendo {paciente.nome}")
        repo.registrar_atendimento(paciente.id, self.id, observacao)
        repo.atualizar_status_paciente(paciente.id, "ATENDIDO")

