from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.db import get_db

bp = Blueprint("assinatura", __name__, url_prefix="/assinatura")

@bp.route("/minha", methods=["GET", "POST"])
@login_required
def minha_assinatura():
    db = get_db()
    if request.method == "POST":
        nome = request.form.get("assinatura_nome")
        fonte = request.form.get("assinatura_fonte")
        if nome and fonte:
            cursor = db.cursor()
            cursor.execute("UPDATE usuarios SET assinatura_nome=%s, assinatura_fonte=%s WHERE id=%s",
                           (nome, fonte, current_user.id))
            db.commit()
            cursor.close()
            flash("Assinatura salva com sucesso!", "success")
            return redirect(url_for("assinatura.minha_assinatura"))
    # busca assinatura atual
    cursor = db.cursor()
    cursor.execute("SELECT assinatura_nome, assinatura_fonte FROM usuarios WHERE id=%s", (current_user.id,))
    row = cursor.fetchone()
    cursor.close()
    assinatura = {"nome": row[0] if row and row[0] else "", "fonte": row[1] if row and row[1] else "Arial"}
    return render_template("minha_assinatura.html", assinatura=assinatura)
