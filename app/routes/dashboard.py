from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.db import get_db

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

# ----------------- DASHBOARD PRINCIPAL -----------------
@bp.route("/")
@login_required
def index():
    db = get_db()
    cursor = db.cursor()
    # Pega apenas documentos recebidos não visualizados
    cursor.execute("""
        SELECT id, nome, data_upload
        FROM documentos
        WHERE destinatario_email=%s AND visualizado=0
        ORDER BY data_upload DESC
        LIMIT 5
    """, (current_user.email,))
    documentos = cursor.fetchall()
    cursor.close()
    return render_template("dashboard.html", documentos_recebidos=documentos)

# ----------------- DOCUMENTOS ENVIADOS -----------------
@bp.route("/enviados")
@login_required
def documentos_enviados():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, nome, data_upload
        FROM documentos
        WHERE id_usuario=%s
        ORDER BY data_upload DESC
        LIMIT 5
    """, (current_user.id,))
    documentos = cursor.fetchall()
    cursor.close()
    return render_template("documentos_enviados.html", documentos_enviados=documentos)

# ----------------- DOCUMENTOS RECEBIDOS -----------------
@bp.route("/recebidos")
@login_required
def documentos_recebidos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, nome, data_upload, visualizado
        FROM documentos
        WHERE destinatario_email=%s
        ORDER BY data_upload DESC
    """, (current_user.email,))
    documentos = cursor.fetchall()
    cursor.close()
    return render_template("documentos_recebidos.html", documentos_recebidos=documentos)

# ----------------- MINHA ASSINATURA -----------------
@bp.route("/assinatura", methods=["GET", "POST"])
@login_required
def minha_assinatura():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT assinatura_nome, assinatura_fonte FROM usuarios WHERE id=%s", (current_user.id,))
    user = cursor.fetchone()
    assinatura = {
        "nome": user["assinatura_nome"] if user and user["assinatura_nome"] else "",
        "fonte": user["assinatura_fonte"] if user and user["assinatura_fonte"] else "Arial"
    }

    if request.method == "POST":
        nome = request.form.get("assinatura_nome")
        fonte = request.form.get("assinatura_fonte")
        cursor.execute("UPDATE usuarios SET assinatura_nome=%s, assinatura_fonte=%s WHERE id=%s",
                       (nome, fonte, current_user.id))
        db.commit()
        flash("Assinatura salva com sucesso!", "success")
        return redirect(url_for("dashboard.minha_assinatura"))

    cursor.close()
    return render_template("minha_assinatura.html", assinatura=assinatura)

# ----------------- PERFIL -----------------
@bp.route("/perfil")
@login_required
def perfil():
    return render_template("perfil.html", user=current_user)
