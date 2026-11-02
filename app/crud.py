from db.connection import conectar

def cadastrar_paciente(cpf, nome, tipo_preferencial, sintomas, classificacao_risco):
    conexao = conectar()
    if not conexao:
        print("Erro ao conectar no banco")
        return False

    try:
        cursor = conexao.cursor()

        # Insere na tabela pacientes
        sql_paciente = """
            INSERT INTO paciente (cpf, nome, tipo_preferencial)
            VALUES (%s, %s, %s)
        """
        cursor.execute(sql_paciente, (cpf, nome, tipo_preferencial))

        # Insere na tabela triagens
        sql_triagem = """
            INSERT INTO triagem 
            (cpf_paciente, sintomas_relatados, classificacao_risco, status)
            VALUES (%s, %s, %s, 'Aguardando')
        """
        cursor.execute(sql_triagem, (cpf, sintomas, classificacao_risco))

        conexao.commit()
        print("Paciente cadastrado com sucesso!")
        return True

    except Exception as erro:
        print(f"Erro ao cadastrar paciente: {erro}")
        conexao.rollback()
        return False

    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

def cadastrar_medico(crm, nome):
    conexao = conectar()
    if not conexao:
        print("Erro ao conectar no banco")
        return False

    try:
        cursor = conexao.cursor()

        sql = """
            INSERT INTO medico (crm, nome)
            VALUES (%s, %s)
        """
        cursor.execute(sql, (crm, nome))
        conexao.commit()

        print("Médico cadastrado com sucesso!")
        return True

    except Exception as erro:
        print(f"Erro ao cadastrar médico: {erro}")
        conexao.rollback()
        return False

    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()            

def listar_fila():
    conexao = conectar()
    if not conexao:
        print("Erro ao conectar no banco")
        return []

    try:
        cursor = conexao.cursor(dictionary=True)

        sql = """
            SELECT 
                t.id_atendimento,
                p.nome AS Nome_Paciente,
                p.tipo_preferencial,
                t.sintomas_relatados,
                t.classificacao_risco,
                t.data_hora_chegada
            FROM triagem t
            JOIN paciente p ON t.cpf_paciente = p.cpf
            WHERE t.status = 'Aguardando'
            ORDER BY 
                CASE t.classificacao_risco
                    WHEN 'Vermelho' THEN 1
                    WHEN 'Amarelo' THEN 2
                    WHEN 'Verde' THEN 3
                    ELSE 4
                END ASC,
                CASE 
                    WHEN p.tipo_preferencial IS NOT NULL THEN 0 
                    ELSE 1 
                END ASC,
                t.data_hora_chegada ASC
        """

        cursor.execute(sql)
        resultados = cursor.fetchall()
        return resultados

    except Exception as erro:
        print(f"Erro ao listar fila: {erro}")
        return []

    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

def atender_paciente(id_atendimento, crm_medico):
    conexao = conectar()
    if not conexao:
        print("Erro ao conectar no banco")
        return False

    try:
        cursor = conexao.cursor()

        sql = """
            UPDATE triagem
            SET status = 'Em Atendimento',
                crm_medico = %s
            WHERE id_atendimento = %s
              AND status = 'Aguardando'
        """
        cursor.execute(sql, (crm_medico, id_atendimento))
        conexao.commit()

        if cursor.rowcount > 0:
            print("Paciente colocado em atendimento!")
            return True
        else:
            print("Nenhum paciente encontrado ou já estava em atendimento.")
            return False

    except Exception as erro:
        print(f"Erro ao atender: {erro}")
        conexao.rollback()
        return False

    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

def finalizar_atendimento(id_atendimento):
    conexao = conectar()
    if not conexao:
        print("Erro ao conectar no banco")
        return False

    try:
        cursor = conexao.cursor()

        sql = """
            UPDATE triagem
            SET status = 'Atendido'
            WHERE id_atendimento = %s
              AND status = 'Em Atendimento'
        """
        cursor.execute(sql, (id_atendimento,))
        conexao.commit()

        if cursor.rowcount > 0:
            print("Atendimento finalizado!")
            return True
        else:
            print("Atendimento não encontrado ou não estava em andamento.")
            return False

    except Exception as erro:
        print(f"Erro ao finalizar: {erro}")
        conexao.rollback()
        return False

    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()            
