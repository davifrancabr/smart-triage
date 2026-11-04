from mysql.connector import IntegrityError, Error

from db.repositorio import RepositorioDB
from ia.ClassificadorIAService import ClassificadorIA
from modelos.constantes import EMOJI
from modelos.medico import Medico
from servicos.triagem import Triagem

MENU = """
===== SMART TRIAGE =====
1 - Cadastrar paciente (triagem)
2 - Ver fila de espera
3 - Chamar próximo paciente (atender)
4 - Ver histórico de atendimentos
5 - Cadastrar médico
6 - Corrigir risco de um paciente
0 - Sair
"""


def ler_inteiro(msg: str) -> int:
    try:
        return int(input(msg).strip())
    except ValueError:
        raise ValueError("Digite um número válido.")


def listar_fila(triagem: Triagem):
    fila = triagem.fila.ordenada()
    if not fila:
        print("Fila de espera vazia.")
        return
    print("\n--- Fila de espera (ordem de atendimento) ---")
    for pos, p in enumerate(fila, start=1):
        print(f"{pos:>2}. [ID {p.id_atendimento}] {EMOJI[p.risco]} {p} | {p.sintomas[:50]}")


def escolher_medico(repo: RepositorioDB):
    medicos = repo.listar_medicos()
    if not medicos:
        print("Nenhum médico cadastrado. Cadastre um primeiro (opção 5).")
        return None

    for m in medicos:
        print(f"  CRM {m.crm} - {m.nome} ({m.especialidade})")

    crm = input("CRM do médico: ").strip()
    escolhido = next((m for m in medicos if m.crm == crm), None)
    if escolhido is None:
        print("CRM não encontrado.")
    return escolhido


def cadastrar_paciente(triagem: Triagem):
    nome = input("Nome: ")
    idade = ler_inteiro("Idade: ")
    cpf = input("CPF (Somente números): ")
    sintomas = input("Sintomas: ")
    motivo = input("Atendimento preferencial? (idoso/gestante/pcd, Enter se não): ").strip()
    paciente, justificativa, origem = triagem.adicionar(
        nome, idade, cpf, sintomas, preferencial_motivo=motivo or None
    )
    print(f"\n{EMOJI[paciente.risco]} Classificado como {paciente.risco} ({origem})")
    print(f"Justificativa: {justificativa}")
    print(f"Atendimento nº {paciente.id_atendimento} registrado.")


def atender(triagem: Triagem, repo: RepositorioDB):
    if triagem.fila.vazia():
        print("Fila de espera vazia.")
        return
    medico = escolher_medico(repo)
    if medico is None:
        return
    obs = input("Observação do atendimento (opcional): ")
    paciente = triagem.chamar_proximo(medico, obs)
    if paciente is None:
        print("Não foi possível atender: a fila mudou. Tente novamente.")
    else:
        print(f"\nAtendido: {EMOJI[paciente.risco]} {paciente} por {medico}")


def mostrar_historico(repo: RepositorioDB):
    historico = repo.historico()
    if not historico:
        print("Nenhum atendimento registrado no sistema.")
        return
    print("\n--- Histórico ---")
    for h in historico:
        medico = h["medico"] or "—"
        emoji = EMOJI[h["risco"].upper()]
        print(f"{h['data_hora_chegada']:%d/%m/%Y %H:%M} | {emoji} {h['paciente']} | "
              f"{h['status']} | Médico: {medico} | {h['observacao'] or ''}")


def cadastrar_medico(repo: RepositorioDB):
    crm = input("CRM: ")
    nome = input("Nome: ")
    especialidade = input("Especialidade: ")
    try:
        repo.cadastrar_medico(Medico(crm, nome, especialidade))
        print("Médico cadastrado.")
    except IntegrityError:
        print("Já existe um médico com esse CRM.")


def corrigir_risco(triagem: Triagem):
    listar_fila(triagem)
    if triagem.fila.vazia():
        return
    id_atendimento = ler_inteiro("ID do atendimento: ")
    novo = input("Novo risco (Vermelho/Amarelo/Verde): ")
    triagem.corrigir_risco(id_atendimento, novo)
    print("Risco atualizado.")
    listar_fila(triagem)


def _loop(repo: RepositorioDB):
    triagem = Triagem(repo, ClassificadorIA())

    acoes = {
        "1": lambda: cadastrar_paciente(triagem),
        "2": lambda: listar_fila(triagem),
        "3": lambda: atender(triagem, repo),
        "4": lambda: mostrar_historico(repo),
        "5": lambda: cadastrar_medico(repo),
        "6": lambda: corrigir_risco(triagem),
    }
    while True:
        print(MENU)
        opcao = input("> ").strip()
        if opcao == "0":
            print("Até logo!")
            return
        acao = acoes.get(opcao)
        if acao is None:
            print("Opção inválida.")
            continue
        try:
            acao()
        except ValueError as erro:
            print(f"Erro: {erro}")
        except Error as erro:
            print(f"Erro: {erro}")


def executar():
    try:
        repo = RepositorioDB()
    except Error as erro:
        print(f"Não foi possível conectar ao banco: {erro}")
        print("Confira o arquivo .env e se o MySQL está rodando (docker compose up -d).")
        return
    try:
        _loop(repo)
    finally:
        repo.fechar()
