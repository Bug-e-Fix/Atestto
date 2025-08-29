# app/routes/documentos.py
import os
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from app.services.db import get_db
from app.services.gov_service import assinar_documento_simulado
from datetime import datetime

documentos = Blueprint("documentos", __name__, url_prefix="/documentos")

UPLOAD_FOLDER = "uploads"
SIGNED_FOLDER = "signed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SIGNED_FOLDER, exist_ok=True)

# ----------------- DOCUMENTOS ENVIADOS -----------------
@documentos.route("/enviados", methods=["GET", "POST"])
@login_required
def enviados():
    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        file = request.files.get("file")
        titulo = request.form.get("titulo") or file.filename
        destinatario = request.form.get("destinatario_email")

        if not file:
            flash("Nenhum arquivo selecionado.", "error")
            return redirect(url_for("documentos.enviados"))

        # Salva o arquivo enviado
        filename = f"{current_user.id}_{file.filename.replace(' ', '_')}"
        uploaded_file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(uploaded_file_path)

        # Assina o documento (simulação Gov.br)
        signed_path = assinar_documento_simulado(current_user, uploaded_file_path, current_user.nome or current_user.email)

        # Salva no banco de dados
        cur.execute(
            """
            INSERT INTO documentos 
            (id_usuario, titulo, nome, conteudo, dados, destinatario_email, data_upload, visualizado, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                current_user.id,
                titulo,
                file.filename,
                None,           # Conteúdo textual opcional
                signed_path,    # Caminho do arquivo assinado
                destinatario or None,
                datetime.utcnow(),
                0,
                "Assinado (simulado)"
            )
        )
        db.commit()
        flash("Documento enviado e assinado com sucesso (simulado).", "success")
        return redirect(url_for("documentos.enviados"))

    # GET: listar documentos enviados
    cur.execute("SELECT * FROM documentos WHERE id_usuario=%s ORDER BY data_upload DESC", (current_user.id,))
    documentos_enviados = cur.fetchall()
    cur.close()
    return render_template("documentos_enviados.html", documentos_enviados=documentos_enviados)
