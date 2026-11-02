from app.db.crud import RepositorioDB
from app.ia.ClassificadorIAService import ClassificadorIA
from app.modelos.constantes import EMOJI
from app.modelos.medico import Medico
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
    repo = RepositorioDB
    triagem = Triagem(repo, ClassificadorIA())

    print(f"Pacientes aguardando... recuperados do banco: {len(triagem.fila)}")

    while True:
        op = menu()

        if op == "1":
            nome = input("Nome: ")
            idade = int(input("Idade: ") or 0)
            sintomas = input("Descreva os sintomas: ")
            motivo = input("Preferencial? (idoso/gestante/pcd ou Enter p/ não): ").strip()
            if not motivo and idade >= 60:
                motivo = "idoso"
            p, just, origem = triagem.adicionar(nome, idade, sintomas, motivo or None)
            print(f"\n{EMOJI[p.risco]} {p}\n  Classificação: {origem}\n  Motivo: {just}")
        elif op == "2":
            itens = triagem.fila.ordenada()
            if not itens:
                print("Fila vazia.")
            for pos, p in enumerate(itens, 1):
                print(f"{pos:>2}. {EMOJI[p.risco]} {p}  | {p.sintomas[:50]}")
        elif op == "3":
            if triagem.fila.vazia():
                print("Fila vazia.")
                continue
            m = escolher_medico(repo)
            if not m:
                print("Médico inválido.")
                continue
            obs = input("Observação do atendimento: ")
            p = triagem.chamarProximo(m, obs)
            print(f"Atendido: {EMOJI[p.risco]} {p} por {m.nome}")
        elif op == "4":
            for h in repo.historico():
                print(f"[{h['data_hora']: %d/%m/%Y %H:%M}] {EMOJI[h['risco']]} {h['paciente']} "
                      f"-> Dr(a). {h['medico']} ({h['especialidade']}) | {h['observacao']})")
        elif op == "5":
            m = Medico(input("Nome do medico: "), input('CPF: '), input('CRM: '), input("Especialidade: "))
        elif op == "6":
            try:
                pid = int(input("ID do paciente: "))
                novo = input("Novo risco (VERMELHO/AMARELO/VERDE): ").strip()
            except ValueError:
                print("Entrada inválida.")
                continue
            triagem.corrigir_risco(pid, novo)
            print("Risco atualizado e fila reorganizada.")
        elif op == "0":
            break
        else:
            print("Opção invalida!")