from app.ia.ClassificadorIAService import ClassificadorIA
from app.servicos.triagem import Triagem


def escolher_medico(repo):
    medicos = repo.listar_medicos()
    if not medicos:
        print("Nenhum médico cadastrado. Cadastre um primeiro (opção 5).")
        return None

    for m in medicos:
        print(f"    {m.id}) {m.nome} - {m.especialidade}")

    try:
        mid = int(input("ID do médico: "))
    except ValueError:
        return None
    return next((m for m in medicos if m.id == mid), None)

def menu():
    print("""
    ===== SMART TRIAGE =====
    1) Registrar paciente
    2) Ver fila de atendimento
    3) Chamar próximo paciente
    4) Histórico de atendimentos
    5) Cadastrar médico
    6) Corrigir risco de paciente na fila
    0) Sair""")
    return input("> ").strip()

def executar():
    repo = ""
    triagem = Triagem(repo, ClassificadorIA())

    print(f"Pacientes aguardando... recuperados do banco: {len(triagem.fila)}")

    while True:
        op = menu()

        if op == 1:
            ...
        elif op == 2:
            ...
        elif op == 3:
            ...
        elif op == 4:
            ...
        elif op == 5:
            ...
        elif op == 6:
            ...
        elif op == 0:
            break
        else:
            print("Opção invalida!")