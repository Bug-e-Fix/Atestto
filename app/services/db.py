# app/services/db.py
import pymysql
from flask import g, current_app

def get_db():
    """
    Retorna a conexão com o banco de dados (armazenada em flask.g).
    Usa pymysql.cursors.DictCursor para retornar dicionários ao buscar.
    NÃO feche a conexão manualmente — ela será fechada no teardown do app.
    """
    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config.get('DB_HOST', 'localhost'),
            user=current_app.config.get('DB_USER', 'root'),
            password=current_app.config.get('DB_PASSWORD', ''),
            database=current_app.config.get('DB_NAME', 'Atestto'),
            port=int(current_app.config.get('DB_PORT', 3306)),
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

def get_db_connection():
    """
    Alias compatível com código antigo que importava get_db_connection.
    Retorna a mesma conexão que get_db().
    """
    return get_db()

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass

def init_db(app):
    """
    Registra o teardown para fechar a conexão ao final de cada request.
    """
    app.teardown_appcontext(close_db)
