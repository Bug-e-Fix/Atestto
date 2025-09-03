# app/routes/dashboard.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, abort, current_app
from flask_login import login_required, current_user
from app.services.db import get_db
from datetime import datetime
from pymysql.cursors import DictCursor

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
SIGNED_FOLDER = os.path.join(os.getcwd(), "signed")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SIGNED_FOLDER, exist_ok=True)


# ----------------- INDEX (dashboard) -----------------
@bp.route("/", methods=["GET"])
@login_required
def index():
    db = get_db()
    cur = db.cursor(DictCursor)
    try:
        cur.execute(
            "SELECT id, id_usuario, titulo, nome, dados, destinatario_email, data_upload, visualizado, status "
            "FROM documentos WHERE destinatario_email=%s ORDER BY data_upload DESC",
            (current_user.email,)
        )
        documentos_recebidos = cur.fetchall() or []
    finally:
        try:
            cur.close()
        except Exception:
            pass

    return render_template("dashboard.html", current_user=current_user, documentos_recebidos=documentos_recebidos)


# ----------------- DOCUMENTOS ENVIADOS -----------------
@bp.route("/documentos/enviados", methods=["GET", "POST"])
@login_required
def documentos_enviados():
    db = get_db()
    cur = db.cursor(DictCursor)
    try:
        if request.method == "POST":
            file = request.files.get("file")
            titulo = request.form.get("titulo") or request.form.get("nome_documento") or "Sem título"
            nome_documento = request.form.get("nome_documento") or (file.filename if file else None)
            destinatario = request.form.get("destinatario_email")

            if not file:
                flash("Nenhum arquivo selecionado.", "error")
                return redirect(url_for("dashboard.documentos_enviados"))

            safe_filename = file.filename.replace(" ", "_")
            filename = f"{current_user.id}_{safe_filename}"
            uploaded_file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(uploaded_file_path)

            cur.execute(
                """
                INSERT INTO documentos
                (id_usuario, titulo, nome, conteudo, dados, destinatario_email, data_upload, visualizado, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    current_user.id,
                    titulo,
                    nome_documento,
                    None,
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

        # GET -> listar documentos enviados pelo usuário
        cur.execute(
            "SELECT id, id_usuario, titulo, nome, dados, destinatario_email, data_upload, visualizado, status "
            "FROM documentos WHERE id_usuario=%s ORDER BY data_upload DESC",
            (current_user.id,)
        )
        documentos_enviados = cur.fetchall() or []
    finally:
        try:
            cur.close()
        except Exception:
            pass

    return render_template("documentos_enviados.html", documentos_enviados=documentos_enviados)


# ----------------- DOCUMENTOS RECEBIDOS -----------------
@bp.route("/documentos/recebidos", methods=["GET"])
@login_required
def documentos_recebidos():
    db = get_db()
    cur = db.cursor(DictCursor)
    try:
        cur.execute(
            "SELECT id, id_usuario, titulo, nome, dados, destinatario_email, data_upload, visualizado, status "
            "FROM documentos WHERE destinatario_email=%s ORDER BY data_upload DESC",
            (current_user.email,)
        )
        documentos_recebidos = cur.fetchall() or []
    finally:
        try:
            cur.close()
        except Exception:
            pass

    return render_template("documentos_recebidos.html", documentos_recebidos=documentos_recebidos)


# ----------------- VISUALIZAR DOCUMENTO -----------------
@bp.route("/documento/<int:doc_id>/visualizar")
@login_required
def visualizar_documento(doc_id):
    db = get_db()
    cur = db.cursor(DictCursor)
    try:
        cur.execute("SELECT id, id_usuario, nome, dados, destinatario_email, titulo, data_upload FROM documentos WHERE id=%s", (doc_id,))
        doc = cur.fetchone()
    finally:
        try:
            cur.close()
        except Exception:
            pass

    if not doc:
        flash("Documento não encontrado.", "danger")
        return redirect(url_for("dashboard.documentos_enviados"))

    # permissões: dono ou destinatário
    owner_id = doc.get("id_usuario")
    try:
        owner_id_int = int(owner_id) if owner_id is not None else None
    except Exception:
        owner_id_int = None

    destinatario_email = doc.get("destinatario_email")
    current_email = (getattr(current_user, "email", "") or "").lower()
    is_owner = (owner_id_int is not None and str(owner_id_int) == str(current_user.id))
    is_recipient = (destinatario_email is not None and current_email and destinatario_email.lower() == current_email)

    if not (is_owner or is_recipient):
        flash("Você não tem permissão para visualizar este documento.", "danger")
        return redirect(url_for("dashboard.documentos_enviados"))

    return render_template("visualizar_documento.html", documento=doc)


# ----------------- Servir PDF inline -----------------
@bp.route("/documento/<int:doc_id>/ver_pdf")
@login_required
def ver_pdf(doc_id):
    db = get_db()
    cur = db.cursor(DictCursor)
    try:
        cur.execute("SELECT id, dados, id_usuario, destinatario_email FROM documentos WHERE id=%s", (doc_id,))
        doc = cur.fetchone()
    finally:
        try:
            cur.close()
        except Exception:
            pass

    if not doc:
        abort(404, "Documento não encontrado.")

    # permissões: dono ou destinatário
    owner_id = doc.get("id_usuario")
    try:
        owner_id_int = int(owner_id) if owner_id is not None else None
    except Exception:
        owner_id_int = None
    destinatario_email = doc.get("destinatario_email")
    current_email = (getattr(current_user, "email", "") or "").lower()
    is_owner = (owner_id_int is not None and str(owner_id_int) == str(current_user.id))
    is_recipient = (destinatario_email is not None and current_email and destinatario_email.lower() == current_email)
    if not (is_owner or is_recipient):
        abort(403)

    arquivo_path = doc.get("dados")
    if isinstance(arquivo_path, (bytes, bytearray)):
        try:
            arquivo_path = arquivo_path.decode("utf-8")
        except Exception:
            arquivo_path = arquivo_path.decode("latin1", errors="ignore")

    arquivo_path = arquivo_path.replace("\\", os.path.sep).strip()
    if not os.path.isabs(arquivo_path):
        arquivo_path = os.path.normpath(os.path.join(os.getcwd(), arquivo_path))

    if not os.path.exists(arquivo_path):
        abort(404, "Arquivo não encontrado no servidor.")

    return send_file(arquivo_path, mimetype="application/pdf", as_attachment=False)


# ----------------- DEFINIR ASSINATURA -----------------
@bp.route("/documento/<int:doc_id>/definir_assinatura", methods=["POST"])
@login_required
def definir_assinatura(doc_id):
    coords = request.get_json(silent=True) or {}
    x = coords.get("x")
    y = coords.get("y")
    pagina = coords.get("pagina")

    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("""
            UPDATE documentos
            SET assinatura_x=%s, assinatura_y=%s, assinatura_pagina=%s
            WHERE id=%s AND id_usuario=%s
        """, (x, y, pagina, doc_id, current_user.id))
        db.commit()
    finally:
        try:
            cur.close()
        except Exception:
            pass

    return jsonify({"message": "Posição da assinatura salva com sucesso"}), 200


# ----------------- CANCELAR ENVIO -----------------
@bp.route("/documento/<int:doc_id>/cancelar", methods=["POST"])
@login_required
def cancelar_envio(doc_id):
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("UPDATE documentos SET status='Cancelado' WHERE id=%s AND id_usuario=%s", (doc_id, current_user.id))
        db.commit()
    finally:
        try:
            cur.close()
        except Exception:
            pass

    flash("Envio cancelado com sucesso.", "info")
    return redirect(url_for("dashboard.documentos_enviados"))


# ----------------- MINHA ASSINATURA -----------------
@bp.route("/assinatura", methods=["GET", "POST"])
@login_required
def minha_assinatura():
    db = get_db()
    cur = db.cursor(DictCursor)
    try:
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
    finally:
        try:
            cur.close()
        except Exception:
            pass

    return render_template("minha_assinatura.html", assinatura=assinatura)


# ----------------- PERFIL -----------------
@bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    db = get_db()
    cur = db.cursor(DictCursor)
    try:
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            if nome:
                cur.execute("UPDATE usuarios SET name=%s WHERE id=%s", (nome, current_user.id))
                db.commit()
                flash("Perfil atualizado com sucesso.", "success")
            return redirect(url_for("dashboard.perfil"))

        cur.execute("SELECT id, name, email, cpf FROM usuarios WHERE id=%s", (current_user.id,))
        usuario = cur.fetchone() or {}
    finally:
        try:
            cur.close()
        except Exception:
            pass

    return render_template("perfil.html", usuario=usuario)
