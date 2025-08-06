# app/models/user.py

from app.extensions import get_db_connection
from flask_login import UserMixin

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
