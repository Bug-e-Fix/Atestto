# app/routes/dashboard.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.db import get_db

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

# DASHBOARD PRINCIPAL - mostra documentos recebidos não visualizados
@bp.route("/")
@login_required
def index():
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, nome, data_upload, visualizado
            FROM documentos
            WHERE destinatario_email=%s AND (visualizado IS NULL OR visualizado=0)
            ORDER BY data_upload DESC
            LIMIT 5
        """, (current_user.email,))
        documentos = cursor.fetchall()
    finally:
        cursor.close()
    return render_template("dashboard.html", current_user=current_user, documentos_recebidos=documentos)


# DOCUMENTOS ENVIADOS (somente listagem - formulário usa blueprint 'documentos' para POST)
@bp.route("/enviados")
@login_required
def documentos_enviados():
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, nome, data_upload, visualizado
            FROM documentos
            WHERE id_usuario=%s
            ORDER BY data_upload DESC
            LIMIT 20
        """, (current_user.id,))
        documentos = cursor.fetchall()
    finally:
        cursor.close()
    return render_template("documentos_enviados.html", current_user=current_user, documentos=documentos)


# DOCUMENTOS RECEBIDOS (tela completa)
@bp.route("/recebidos")
@login_required
def documentos_recebidos():
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, nome, data_upload, visualizado
            FROM documentos
            WHERE destinatario_email=%s
            ORDER BY data_upload DESC
        """, (current_user.email,))
        documentos = cursor.fetchall()
    finally:
        cursor.close()
    return render_template("documentos_recebidos.html", current_user=current_user, documentos=documentos)


# PERFIL - agora passa `user` como dict para o template
@bp.route("/perfil")
@login_required
def perfil():
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, email, cpf, assinatura_nome, assinatura_fonte FROM usuarios WHERE id=%s", (current_user.id,))
        row = cursor.fetchone()
    finally:
        cursor.close()
    # row é dict (por conta do DictCursor). Se for None, passa dict vazio.
    return render_template("perfil.html", current_user=current_user, user=row or {})


# MINHA ASSINATURA (rota sob 'dashboard' — template deve chamar url_for('dashboard.minha_assinatura'))
@bp.route("/assinatura", methods=["GET", "POST"])
@login_required
def minha_assinatura():
    conn = get_db()
    if request.method == "POST":
        assinatura_nome = request.form.get("assinatura_nome", "").strip()
        assinatura_fonte = request.form.get("assinatura_fonte", "Arial").strip()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE usuarios SET assinatura_nome=%s, assinatura_fonte=%s WHERE id=%s",
                        (assinatura_nome, assinatura_fonte, current_user.id))
            conn.commit()
            flash("Assinatura salva.", "success")
        finally:
            cur.close()
        return redirect(url_for("dashboard.minha_assinatura"))

    cur = conn.cursor()
    try:
        cur.execute("SELECT assinatura_nome, assinatura_fonte FROM usuarios WHERE id=%s", (current_user.id,))
        row = cur.fetchone()
    finally:
        cur.close()

    assinatura = {
        "nome": row.get("assinatura_nome") if row else "",
        "fonte": row.get("assinatura_fonte") if row else "Arial"
    }
    return render_template("minha_assinatura.html", current_user=current_user, assinatura=assinatura)
