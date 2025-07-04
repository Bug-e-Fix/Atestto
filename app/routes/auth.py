from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app.models.user import (
    get_user_by_email,
    create_user,
    update_user_confirmation,
    update_user_password
)
from app.services.email_service import enviar_email
from app.extensions import csrf

auth_bp = Blueprint('auth', __name__)

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirmation')

def confirm_token(token, expiration=3600*24):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.loads(token, salt='email-confirmation', max_age=expiration)

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset')

def confirm_reset_token(token, expiration=3600*24):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.loads(token, salt='password-reset', max_age=expiration)

def send_confirmation_email(user):
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    html = render_template('emails/confirm_email.html', user=user, confirm_url=confirm_url)
    enviar_email(destinatario=user.email, assunto='Confirme seu e-mail - Atestto', corpo=html)

def send_reset_email(user):
    token = generate_reset_token(user.email)
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    html = render_template('emails/reset_password.html', user=user, reset_url=reset_url)
    enviar_email(destinatario=user.email, assunto='Redefina sua senha - Atestto', corpo=html)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([name, email, password, confirm_password]):
            flash('Preencha todos os campos', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('As senhas não conferem', 'error')
            return render_template('register.html')

        if get_user_by_email(email):
            flash('Email já cadastrado', 'error')
            return render_template('register.html')

        user = create_user(name, email, password)
        if user:
            send_confirmation_email(user)
            return render_template('aguarde_confirmacao.html', email=email)
        else:
            flash('Erro ao cadastrar usuário', 'error')

    return render_template('register.html')

@auth_bp.route('/confirmar-email/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except SignatureExpired:
        flash('O link de confirmação expirou. Solicite um novo.', 'danger')
        return redirect(url_for('auth.login'))
    except BadSignature:
        flash('Link de confirmação inválido.', 'danger')
        return redirect(url_for('auth.login'))

    user = get_user_by_email(email)
    if user:
        if not user.email_confirmed:
            update_user_confirmation(user.id)
            flash('E-mail confirmado com sucesso!', 'success')
        else:
            flash('E-mail já confirmado.', 'info')
    else:
        flash('Usuário não encontrado.', 'warning')

    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        user = get_user_by_email(email)
        if user and user.check_password(senha):
            if not user.email_confirmed:
                flash('Ative seu e-mail antes de acessar o sistema.', 'warning')
                return render_template('aguarde_confirmacao.html', email=email)
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        else:
            erro = 'Credenciais inválidas'

    return render_template('login.html', erro=erro)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        user = get_user_by_email(email)

        flash('Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha.', 'info')

        if user:
            send_reset_email(user)

        return redirect(url_for('auth.login'))

    return render_template('esqueci_senha.html')

@auth_bp.route('/reset-senha/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = confirm_reset_token(token)
    except SignatureExpired:
        flash('O link para redefinir a senha expirou. Solicite um novo.', 'danger')
        return redirect(url_for('auth.esqueci_senha'))
    except BadSignature:
        flash('Link inválido para redefinir a senha.', 'danger')
        return redirect(url_for('auth.esqueci_senha'))

    user = get_user_by_email(email)
    if not user:
        flash('Usuário não encontrado.', 'warning')
        return redirect(url_for('auth.esqueci_senha'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or not confirm_password:
            flash('Preencha todos os campos.', 'error')
            return render_template('reset_password.html', token=token)

        if password != confirm_password:
            flash('As senhas não conferem.', 'error')
            return render_template('reset_password.html', token=token)

        update_user_password(user.id, password)
        flash('Senha redefinida com sucesso! Faça login com a nova senha.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)

@auth_bp.route('/reenviar-confirmacao', methods=['POST'])
@csrf.exempt
def reenviar_confirmacao():
    email = request.form.get('email')
    user = get_user_by_email(email)

    if user:
        if user.email_confirmed:
            flash('Seu e-mail já está confirmado.', 'info')
        else:
            send_confirmation_email(user)
            flash('E-mail de confirmação reenviado!', 'success')
    else:
        flash('E-mail não encontrado.', 'warning')

    return render_template('aguarde_confirmacao.html', email=email)
