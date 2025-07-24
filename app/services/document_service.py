import pymysql
from config import Config
from app.services.database import get_connection

def get_db_connection():
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        db=Config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def get_documentos_enviados(user_id):
    """
    Retorna os documentos enviados pelo usuário (pelo id).
    """
    query = """
        SELECT id, titulo AS nome, data_upload, status
        FROM documentos
        WHERE id_usuario = %s
        ORDER BY data_upload DESC
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id,))
            return cursor.fetchall()

def get_documentos_recebidos(user_email):
    """
    Retorna os documentos recebidos por um usuário (baseado no e-mail).
    """
    query = """
        SELECT d.id, d.titulo, d.data_upload, d.status, u.email AS remetente_email
        FROM documentos d
        JOIN usuario_has_documento uh ON uh.id_documento = d.id
        JOIN usuario u ON u.id = d.id_usuario
        JOIN usuario dest ON dest.id = uh.id_usuario
        WHERE dest.email = %s
        ORDER BY d.data_upload DESC
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_email,))
            documentos = cursor.fetchall()
        return documentos
    finally:
        conn.close()

def get_documento_por_id(doc_id):
    query = "SELECT id, titulo, dados, data_upload, status FROM documentos WHERE id = %s"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (doc_id,))
            return cursor.fetchone()

def salvar_destinatarios_e_assinatura(doc_id, lista_destinatarios, posicoes):
    """
    Salva os destinatários e suas posições de assinatura para um documento.
    lista_destinatarios: lista de e-mails.
    posicoes: lista de tuplas (pos_x, pos_y) na mesma ordem dos destinatários.
    """
    if len(lista_destinatarios) != len(posicoes):
        raise ValueError("A lista de destinatários e posições devem ter o mesmo tamanho")

    with get_connection() as conn:
        with conn.cursor() as cursor:
            
            cursor.execute("DELETE FROM destinatarios_assinatura WHERE id_documento = %s", (doc_id,))

            
            for email, (pos_x, pos_y) in zip(lista_destinatarios, posicoes):
                cursor.execute(
                    "INSERT INTO destinatarios_assinatura (id_documento, email_destinatario, pos_x, pos_y) VALUES (%s, %s, %s, %s)",
                    (doc_id, email, pos_x, pos_y)
                )
        conn.commit()
