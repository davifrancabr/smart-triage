from app.modelos.pessoa import Pessoa


class Medico(Pessoa):
    def __init__(self, crm: str, nome: str, especialidade: str):
        super().__init__(nome)
        crm = (crm or "").strip()
        if not crm:
            raise ValueError("O CRM não pode ser vazio.")
        self._especialidade = (especialidade or "").strip() or "Clínico Geral"
        self._crm = crm

    @property
    def crm(self) -> str:
        return self._crm

    @property
    def especialidade(self) -> str:
        return self._especialidade

    def atender(self, paciente, repo, observacao: str = "") -> bool:
        return repo.atender_paciente(paciente.id_atendimento, self._crm, observacao)

    def __str__(self) -> str:
        return f"Dr(a). {self.nome} - CRM {self._crm} ({self._especialidade})"