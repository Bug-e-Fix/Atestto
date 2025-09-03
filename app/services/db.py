# app/services/db.py
import pymysql
from pymysql.cursors import DictCursor
from flask import g, current_app

def get_db():
    """
    Retorna uma conexão PyMySQL armazenada em flask.g.
    A conexão é criada na primeira chamada por request e reutilizada
    até o final do request.
    A opção cursorclass=DictCursor faz com que cursors por padrão já
    retornem dicionários (doc['id'], doc['titulo'], etc).
    """
    if "db" not in g:
        g.db = pymysql.connect(
            host=current_app.config.get("DB_HOST", "localhost"),
            user=current_app.config.get("DB_USER", "root"),
            password=current_app.config.get("DB_PASSWORD", ""),
            database=current_app.config.get("DB_NAME", ""),
            port=int(current_app.config.get("DB_PORT", 3306)),
            cursorclass=DictCursor,
            charset="utf8mb4",
            autocommit=False
        )
    return g.db

def close_db(e=None):
    """
    Fecha a conexão armazenada em g (se existir).
    Deve ser registrada com app.teardown_appcontext(close_db).
    """
    db = g.pop("db", None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass
