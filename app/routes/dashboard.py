from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.document_service import get_documentos_enviados, get_documentos_recebidos
from app.services.assinatura_service import salvar_assinatura_usuario, get_assinatura_usuario
from app.models.user import salvar_assinatura_usuario


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

@dashboard_bp.route('/minha-assinatura', methods=['GET', 'POST'])
@login_required
def minha_assinatura():
    if request.method == 'POST':
        nome = request.form['nome']
        fonte = request.form['fonte']
        cpf = request.form['cpf']

        partes = nome.split()
        rubrica = ''
        if len(partes) >= 2:
            rubrica = partes[0][0].upper() + partes[-1][0].upper()

        salvar_assinatura_usuario(current_user.id, nome, fonte, rubrica, cpf)
        flash('Assinatura salva com sucesso!')
        return redirect(url_for('dashboard.minha_assinatura'))

    dados = get_assinatura_usuario(current_user.id)
    return render_template('minha_assinatura.html', dados=dados)
