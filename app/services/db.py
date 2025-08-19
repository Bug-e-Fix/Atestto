# app/db.py
import pymysql
from flask import g, current_app

def get_db():
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

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    app.teardown_appcontext(close_db)
