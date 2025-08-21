from flask import Blueprint, render_template
from flask_login import login_required, current_user

# Blueprint correto
bp = Blueprint("documentos", __name__, url_prefix="/documentos")

# Rota de documentos enviados
@bp.route("/enviados")
@login_required
def enviados():
    # Aqui você pode buscar os documentos enviados no DB
    documentos = []  # Exemplo: lista vazia
    return render_template("documentos_enviados.html", documentos=documentos, current_user=current_user)

# Rota de documentos recebidos
@bp.route("/recebidos")
@login_required
def recebidos():
    # Aqui você pode buscar os documentos recebidos no DB
    documentos = []  # Exemplo: lista vazia
    return render_template("documentos_recebidos.html", documentos=documentos, current_user=current_user)
