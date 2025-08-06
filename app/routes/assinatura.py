from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.assinatura_service import salvar_assinatura_usuario, get_assinatura_usuario

assinatura_bp = Blueprint('assinatura', __name__)

@assinatura_bp.route('/minha-assinatura', methods=['GET','POST'])
@login_required
def minha_assinatura():
    dados = get_assinatura_usuario(current_user.id)
    if request.method=='POST':
        nome  = request.form.get('nome','').strip()
        fonte = request.form.get('fonte','').strip()
        cpf   = request.form.get('cpf','').strip()
        partes = nome.split()
        rubrica = (partes[0][0]+partes[-1][0]).upper() if len(partes)>=2 else ''
        if not all([nome,fonte,cpf]):
            flash('Preencha todos campos','error')
        else:
            salvar_assinatura_usuario(current_user.id,nome,fonte,rubrica,cpf)
            flash('Assinatura salva','success')
            return redirect(url_for('assinatura.minha_assinatura'))
    return render_template('minha_assinatura.html',dados=dados)
