# app/routes/documentos.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.services.db import get_db
from datetime import datetime

bp = Blueprint("documentos", __name__, url_prefix="/documentos")

ALLOWED_EXT = {"pdf", "doc", "docx", "jpg", "png"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@bp.route("/enviados", methods=["GET", "POST"])
@login_required
def enviados():
    conn = get_db()

    if request.method == "POST":
        f = request.files.get("file")
        destinatario = request.form.get("destinatario_email", "").strip()
        nome_documento = request.form.get("nome_documento") or (f.filename if f else None)

        if not f or f.filename == "":
            flash("Selecione um arquivo para enviar.", "warning")
            return redirect(url_for("dashboard.index"))

        if not allowed_file(f.filename):
            flash(f"Tipo de arquivo não permitido. Permitidos: {', '.join(ALLOWED_EXT)}", "warning")
            return redirect(url_for("dashboard.index"))

        uploads_dir = current_app.config.get("UPLOAD_FOLDER") or os.path.join(current_app.root_path, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)

        filename = secure_filename(f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{f.filename}")
        filepath = os.path.join(uploads_dir, filename)
        f.save(filepath)

        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO documentos (id_usuario, nome, arquivo_path, destinatario_email, data_upload, visualizado) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                (current_user.id, nome_documento, filepath, destinatario or None, datetime.utcnow(), 0)
            )
            conn.commit()
            flash("Arquivo enviado com sucesso!", "success")
        finally:
            cur.close()

        return redirect(url_for("documentos.enviados"))

    # GET: lista documentos enviados do usuário
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, nome, data_upload, visualizado FROM documentos WHERE id_usuario=%s ORDER BY data_upload DESC", (current_user.id,))
        documentos = cur.fetchall()
    finally:
        cur.close()

    return render_template("documentos_enviados.html", current_user=current_user, documentos=documentos)


@bp.route("/recebidos")
@login_required
def recebidos():
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, nome, data_upload, visualizado FROM documentos WHERE destinatario_email=%s ORDER BY data_upload DESC", (current_user.email,))
        documentos = cur.fetchall()
    finally:
        cur.close()
    return render_template("documentos_recebidos.html", current_user=current_user, documentos=documentos)
