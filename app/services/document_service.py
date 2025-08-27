# app/routes/documentos.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services.db import get_db

bp = Blueprint("documentos", __name__, url_prefix="/documentos")

@bp.route("/enviados")
@login_required
def enviados():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, nome, data_upload FROM documentos WHERE id_usuario=%s ORDER BY data_upload DESC LIMIT 10", (current_user.id,))
    docs = cursor.fetchall()
    cursor.close()
    return render_template("documentos_enviados.html", documentos=docs)

@bp.route("/recebidos")
@login_required
def recebidos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, nome, data_upload FROM documentos WHERE destinatario_email=%s ORDER BY data_upload DESC LIMIT 10", (current_user.email,))
    docs = cursor.fetchall()
    cursor.close()
    return render_template("documentos_recebidos.html", documentos=docs)
