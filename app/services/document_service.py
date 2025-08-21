from app.services.db import get_db_connection

def get_last_received_documents(user_email, limit=5):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT nome AS nome_arquivo, DATE_FORMAT(data_upload, '%%d/%%m/%%Y') AS data_envio
        FROM documentos
        WHERE destinatario_email = %s
        ORDER BY data_upload DESC
        LIMIT %s
        """,
        (user_email, limit)
    )
    documentos = cursor.fetchall()
    cursor.close()
    db.close()
    return documentos

def get_last_sent_documents(user_id, limit=5):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT nome AS nome_arquivo, DATE_FORMAT(data_upload, '%%d/%%m/%%Y') AS data_envio
        FROM documentos
        WHERE id_usuario = %s
        ORDER BY data_upload DESC
        LIMIT %s
        """,
        (user_id, limit)
    )
    documentos = cursor.fetchall()
    cursor.close()
    db.close()
    return documentos
