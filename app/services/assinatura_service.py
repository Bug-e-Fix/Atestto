from app.services.database import get_connection

def salvar_assinatura_usuario(user_id, nome, fonte, rubrica, cpf):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO assinatura_config (usuario_id, nome, fonte, rubrica, cpf)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    nome = VALUES(nome),
                    fonte = VALUES(fonte),
                    rubrica = VALUES(rubrica),
                    cpf = VALUES(cpf)
            """
            cursor.execute(sql, (user_id, nome, fonte, rubrica, cpf))
        conn.commit()
    finally:
        conn.close()

def get_assinatura_usuario(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT nome, fonte, rubrica, cpf FROM assinatura_config WHERE usuario_id = %s"
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            return row if row else {}
    finally:
        conn.close()
