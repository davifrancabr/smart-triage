import mysql.connector
from mysql.connector import Error

def conectar():
    """
    Cria e retorna uma conexão com o banco de dados MySQL.
    """
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="root", 
            database="triage_smart"
        )

        if conexao.is_connected():
            print("Conexão realizada com sucesso!")
            return conexao

    except Error as erro:
        print(f"Erro ao conectar: {erro}")
        return None
