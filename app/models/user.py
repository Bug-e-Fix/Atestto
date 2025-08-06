# app/models/user.py

from app.extensions import get_db_connection
from flask_login import UserMixin
from datetime import datetime, timedelta

def apagar_usuarios_nao_confirmados(expiracao_horas=24):
    connection = get_db_connection()
    cursor = connection.cursor()

    limite_tempo = datetime.now() - timedelta(hours=expiracao_horas)
    cursor.execute(
        "DELETE FROM usuarios WHERE confirmado = 0 AND criado_em < %s",
        (limite_tempo,)
    )

    connection.commit()
    cursor.close()
    connection.close()


class User(UserMixin):
    def __init__(self, id, nome, email):
        self.id = id
        self.nome = nome
        self.email = email

    @staticmethod
    def get(user_id):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, nome, email FROM usuarios WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        connection.close()
        if row:
            return User(id=row[0], nome=row[1], email=row[2])
        return None


def get_user_by_email(email):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, nome, email FROM usuarios WHERE email = %s", (email,))
    row = cursor.fetchone()
    connection.close()
    if row:
        return User(id=row[0], nome=row[1], email=row[2])
    return None


def create_user(nome, email, senha=None, google_login=False):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, google_login) VALUES (%s, %s, %s, %s)",
        (nome, email, senha, google_login)
    )
    connection.commit()
    user_id = cursor.lastrowid
    connection.close()
    return User(id=user_id, nome=nome, email=email)


def update_user_confirmation(email):
    """
    Marca o usuário como confirmado (confirmado = 1) baseado no e-mail.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        "UPDATE usuarios SET confirmado = 1 WHERE email = %s",
        (email,)
    )
    
    connection.commit()
    cursor.close()
    connection.close()


def update_user_password(email, nova_senha):
    """
    Atualiza a senha do usuário baseado no e-mail.
    Você pode adaptar para receber o ID ao invés do e-mail, se preferir.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        "UPDATE usuarios SET senha = %s WHERE email = %s",
        (nova_senha, email)
    )
    
    connection.commit()
    cursor.close()
    connection.close()
