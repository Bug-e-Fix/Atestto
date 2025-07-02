import pymysql
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.services.database import get_connection

class User(UserMixin):
    def __init__(self, id, name, email, password_hash, email_confirmed=False, created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.email_confirmed = email_confirmed  
        self.created_at = created_at  

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

def get_user_by_email(email):
    conn = get_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM usuario WHERE email = %s"
            cursor.execute(sql, (email,))
            row = cursor.fetchone()
            if row:
                return User(
                    row['id'],
                    row['name'],
                    row['email'],
                    row['password_hash'],
                    row.get('email_confirmed', False),
                    row.get('created_at')
                )
            return None
    finally:
        conn.close()

def get_user_by_id(user_id):
    conn = get_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM usuario WHERE id = %s"
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            if row:
                return User(
                    row['id'],
                    row['name'],
                    row['email'],
                    row['password_hash'],
                    row.get('email_confirmed', False),
                    row.get('created_at')
                )
            return None
    finally:
        conn.close()

def create_user(name, email, password):
    user = User(None, name, email, None)
    user.set_password(password)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO usuario (name, email, password_hash, email_confirmed)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (user.name, user.email, user.password_hash, False))
        conn.commit()
        user.id = cursor.lastrowid
        return user
    except pymysql.err.IntegrityError:
        return None
    finally:
        conn.close()

def update_user_confirmation(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE usuario SET email_confirmed = %s WHERE id = %s"
            cursor.execute(sql, (True, user_id))
        conn.commit()
    finally:
        conn.close()

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


def apagar_usuarios_nao_confirmados(expiracao_horas=24):
    limite = datetime.utcnow() - timedelta(hours=expiracao_horas)
    limite_str = limite.strftime('%Y-%m-%d %H:%M:%S')  

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                DELETE FROM usuario
                WHERE email_confirmed = FALSE
                AND created_at < %s
            """
            cursor.execute(sql, (limite_str,))
        conn.commit()
    finally:
        conn.close()
