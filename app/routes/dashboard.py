from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services.document_service import get_documentos_enviados, get_documentos_recebidos

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    documentos = get_documentos_enviados(current_user.id)
    return render_template('dashboard.html', documentos=documentos)

@dashboard_bp.route('/documentos-enviados')
@login_required
def documentos_enviados():
    documentos = get_documentos_enviados(current_user.id)
    return render_template('documentos_enviados.html', documentos=documentos)

@dashboard_bp.route('/documentos-recebidos')
@login_required
def documentos_recebidos():
    documentos = get_documentos_recebidos(current_user.id)
    return render_template('documentos_recebidos.html', documentos=documentos)

@dashboard_bp.route('/minha-assinatura')
@login_required
def minha_assinatura():
    # Aqui você vai buscar dados da assinatura do usuário para mostrar na página
    return render_template('minha_assinatura.html')
