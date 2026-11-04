class ClassificadorFalso:
    def __init__(self, riscos=None, padrao="VERDE"):
        self.riscos = riscos or {}
        self.padrao = padrao

    def analisar_sintomas(self, sintomas):
        return {"risco": self.riscos.get(sintomas, self.padrao),
                "justificativa": "teste", "origem": "FAKE"}


class RepoFalso:

    def __init__(self):
        self._itens = []
        self._proximo_id = 1
        self.falhar_ao_atender = False

    def registrar_chegada(self, p):
        if any(i[0].cpf == p.cpf and i[1] in ("Aguardando", "Em Atendimento") for i in self._itens):
            raise ValueError("Este paciente já possui uma triagem em andamento.")
        p.id_atendimento = self._proximo_id
        self._proximo_id += 1
        self._itens.append([p, "Aguardando"])
        return p.id_atendimento

    def pacientes_aguardando(self):
        return [p for p, status in self._itens if status == "Aguardando"]

    def atender_paciente(self, id_atendimento, crm, observacao=""):
        if self.falhar_ao_atender:
            return False
        for item in self._itens:
            if item[0].id_atendimento == id_atendimento and item[1] == "Aguardando":
                item[1] = "Atendido"
                return True
        return False

    def atualizar_risco(self, id_atendimento, novo_risco):
        for p, status in self._itens:
            if p.id_atendimento == id_atendimento and status == "Aguardando":
                p.risco = novo_risco
                return True
        return False

    def status_de(self, id_atendimento):
        return next(s for p, s in self._itens if p.id_atendimento == id_atendimento)
