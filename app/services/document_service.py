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
        SELECT titulo AS nome, data_upload, status
        FROM documentos
        WHERE id_usuario = %s
        ORDER BY data_upload DESC
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id,))
            return cursor.fetchall()

def get_documentos_recebidos(user_email):
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
