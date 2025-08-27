# app/services/db.py
from flask import g, current_app
import pymysql
import pymysql.cursors

def get_db():
    if "db" not in g:
        g.db = pymysql.connect(
            host=current_app.config["DB_HOST"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASSWORD"],
            database=current_app.config["DB_NAME"],
            port=int(current_app.config.get("DB_PORT", 3306)),
            cursorclass=pymysql.cursors.DictCursor  # garante dict rows por padrão
        )
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
