from app.modelos.pessoa import Pessoa


class Medico(Pessoa):
    def __init__(self,  crm: str, nome, especialidade: str, id_=None):
        super().__init__(nome)
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

    def atender(self, p, repo, observacao=""):
        print(f"Dr(a). {self.nome} está atendendo {p.nome}")
        repo.registrar_atendimento(self, p)
        repo.atualizar_status_paciente(self, p)
