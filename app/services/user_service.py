from app.services.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
import pymysql

def create_user(nome, email, senha):
    db = get_db()
    cursor = db.cursor()
    hashed = generate_password_hash(senha)
    cursor.execute(
        "INSERT INTO usuarios (name, email, senha) VALUES (%s, %s, %s)",
        (nome, email, hashed)
    )
    db.commit()
    cursor.close()

def verify_user(email, senha):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    if user and check_password_hash(user['senha'], senha):
        return User(user['id'], user['name'], user['email'], user['confirmed'])
    return None

def get_user_by_email(email):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(user['id'], user['name'], user['email'], user['confirmed'])
    return None
