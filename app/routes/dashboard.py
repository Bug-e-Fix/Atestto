# app/routes/dashboard.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.services.db import get_db
from datetime import datetime

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

UPLOAD_FOLDER = "uploads"
SIGNED_FOLDER = "signed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SIGNED_FOLDER, exist_ok=True)

# ----------------- DASHBOARD INDEX -----------------
@bp.route("/")
@login_required
def index():
    return render_template("dashboard.html", current_user=current_user)


# ----------------- DOCUMENTOS ENVIADOS -----------------
@bp.route("/documentos/enviados", methods=["GET", "POST"])
@login_required
def documentos_enviados():
    db = get_db()
    cur = db.cursor()
    
    if request.method == "POST":
        file = request.files.get("file")
        nome_documento = request.form.get("nome_documento") or (file.filename if file else None)
        destinatario = request.form.get("destinatario_email")

        if not file:
            flash("Nenhum arquivo selecionado.", "error")
            return redirect(url_for("dashboard.documentos_enviados"))

        filename = f"{current_user.id}_{file.filename.replace(' ', '_')}"
        uploaded_file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(uploaded_file_path)

        # Salva no banco
        cur.execute(
            """
            INSERT INTO documentos
            (id_usuario, titulo, nome, conteudo, dados, destinatario_email, data_upload, visualizado, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                current_user.id,
                nome_documento,  # título
                nome_documento,
                None,  # conteúdo textual opcional
                uploaded_file_path,
                destinatario or None,
                datetime.utcnow(),
                0,
                "Enviado"
            )
        )
        db.commit()
        flash("Documento enviado com sucesso.", "success")
        return redirect(url_for("dashboard.documentos_enviados"))

    cur.execute(
        "SELECT * FROM documentos WHERE id_usuario=%s ORDER BY data_upload DESC", 
        (current_user.id,)
    )
    documentos_enviados = cur.fetchall()
    cur.close()
    return render_template("documentos_enviados.html", documentos_enviados=documentos_enviados)


# ----------------- DOCUMENTOS RECEBIDOS -----------------
@bp.route("/documentos/recebidos")
@login_required
def documentos_recebidos():
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM documentos WHERE destinatario_email=%s ORDER BY data_upload DESC",
        (current_user.email,)
    )
    documentos_recebidos = cur.fetchall()
    cur.close()
    return render_template("documentos_recebidos.html", documentos_recebidos=documentos_recebidos)


# ----------------- VISUALIZAR DOCUMENTO -----------------
@bp.route("/documento/<int:doc_id>/visualizar")
@login_required
def visualizar_documento(doc_id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT dados, nome FROM documentos WHERE id=%s AND id_usuario=%s",
        (doc_id, current_user.id)
    )
    doc = cur.fetchone()
    cur.close()

    if not doc or not doc.get("dados"):
        flash("Documento não encontrado.", "danger")
        return redirect(url_for("dashboard.documentos_enviados"))

    arquivo_path = doc["dados"]
    if not os.path.exists(arquivo_path):
        flash("Arquivo não encontrado no servidor.", "danger")
        return redirect(url_for("dashboard.documentos_enviados"))

    return send_file(
        arquivo_path,
        as_attachment=True,
        download_name=doc.get("nome") or os.path.basename(arquivo_path)
    )


# ----------------- MINHA ASSINATURA -----------------
@bp.route("/assinatura", methods=["GET", "POST"])
@login_required
def minha_assinatura():
    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        assinatura = request.files.get("assinatura")
        rubrica = request.files.get("rubrica")

        if assinatura:
            assinatura_path = os.path.join(SIGNED_FOLDER, f"{current_user.id}_assinatura.png")
            assinatura.save(assinatura_path)
            cur.execute(
                "INSERT INTO assinaturas (id_usuario, assinatura_path) VALUES (%s, %s) "
                "ON DUPLICATE KEY UPDATE assinatura_path=%s",
                (current_user.id, assinatura_path, assinatura_path)
            )

        if rubrica:
            rubrica_path = os.path.join(SIGNED_FOLDER, f"{current_user.id}_rubrica.png")
            rubrica.save(rubrica_path)
            cur.execute(
                "INSERT INTO assinaturas (id_usuario, rubrica_path) VALUES (%s, %s) "
                "ON DUPLICATE KEY UPDATE rubrica_path=%s",
                (current_user.id, rubrica_path, rubrica_path)
            )

        db.commit()
        flash("Assinatura e rubrica atualizadas com sucesso.", "success")
        return redirect(url_for("dashboard.minha_assinatura"))

    cur.execute("SELECT * FROM assinaturas WHERE id_usuario=%s", (current_user.id,))
    assinatura = cur.fetchone()
    cur.close()
    return render_template("minha_assinatura.html", assinatura=assinatura)


# ----------------- PERFIL -----------------
@bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        cur.execute("UPDATE usuarios SET name=%s WHERE id=%s", (nome, current_user.id))
        db.commit()
        flash("Perfil atualizado com sucesso.", "success")
        return redirect(url_for("dashboard.perfil"))

    cur.execute("SELECT * FROM usuarios WHERE id=%s", (current_user.id,))
    usuario = cur.fetchone()
    cur.close()
    return render_template("perfil.html", usuario=usuario)
