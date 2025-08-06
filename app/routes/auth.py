# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash
from app.models.user import (
    User,
    get_user_by_email,
    create_user,
    update_user_confirmation,
    update_user_password
)
from app.services.email_service import enviar_email
from app.extensions import csrf

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Token serializers
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirmation')

def confirm_token(token, expiration=3600*24):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.loads(token, salt='email-confirmation', max_age=expiration)

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset')

def confirm_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.loads(token, salt='password-reset', max_age=expiration)

# Envio de e-mails
def send_confirmation_email(user):
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    html = render_template('emails/confirm_email.html', user=user, confirm_url=confirm_url)
    enviar_email(destinatario=user.email, assunto='Confirme seu e-mail - Atestto', corpo_html=html)

def send_reset_email(user):
    token = generate_reset_token(user.email)
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    html = render_template('emails/reset_password.html', user=user, reset_url=reset_url)
    enviar_email(destinatario=user.email, assunto='Redefina sua senha - Atestto', corpo_html=html)

# Registro
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        cpf = request.form.get('cpf')
        tipo_assinatura = request.form.get('tipo_assinatura')

        if not all([name, email, password, confirm_password, cpf, tipo_assinatura]):
            flash('Preencha todos os campos.', 'error')
            return render_template('register.html', name=name, email=email, cpf=cpf, tipo_assinatura=tipo_assinatura)

        if password != confirm_password:
            flash('As senhas não conferem.', 'error')
            return render_template('register.html', name=name, email=email, cpf=cpf, tipo_assinatura=tipo_assinatura)

        if get_user_by_email(email):
            flash('E-mail já cadastrado.', 'error')
            return render_template('register.html', name=name, email=email, cpf=cpf, tipo_assinatura=tipo_assinatura)

        hashed_password = generate_password_hash(password)
        user = create_user(name, email, hashed_password, cpf, tipo_assinatura)

        if user:
            send_confirmation_email(user)
            flash('Cadastro realizado! Verifique seu e-mail para confirmar sua conta.', 'success')
            return render_template('aguarde_confirmacao.html', email=email)
        else:
            flash('Erro ao cadastrar usuário. Tente novamente.', 'error')

    return render_template('register.html')

# Confirmação de e-mail
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
        if not user.confirmed:
            update_user_confirmation(user.id)
            flash('E-mail confirmado com sucesso! Você já pode fazer login.', 'success')
        else:
            flash('E-mail já confirmado.', 'info')
    else:
        flash('Usuário não encontrado.', 'warning')

    return redirect(url_for('auth.login'))

# Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password_from_form = request.form.get('password')

        user = get_user_by_email(email)
        if user and user.check_password(password_from_form):
            if not user.confirmed:
                flash('Ative seu e-mail antes de acessar o sistema.', 'warning')
                return render_template('aguarde_confirmacao.html', email=email)
            login_user(user)
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Credenciais inválidas.', 'danger')

    return render_template('login.html')

# Logout
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('auth.login'))

# Esqueci minha senha
@auth_bp.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        user = get_user_by_email(email)

        if user:
            send_reset_email(user)
            flash('Se o e-mail estiver cadastrado, um link para redefinir a senha foi enviado para você.', 'info')
        else:
            flash('E-mail não encontrado.', 'danger')

        return redirect(url_for('auth.login'))

    return render_template('esqueci_senha.html')

# Redefinir senha
@auth_bp.route('/reset-senha/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = confirm_reset_token(token)
    except SignatureExpired:
        flash('O link para redefinir a senha expirou.', 'danger')
        return redirect(url_for('auth.esqueci_senha'))
    except BadSignature:
        flash('Link inválido.', 'danger')
        return redirect(url_for('auth.esqueci_senha'))

    user = get_user_by_email(email)
    if not user:
        flash('Usuário não encontrado.', 'warning')
        return redirect(url_for('auth.esqueci_senha'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        cpf_input = request.form.get('cpf')
        tipo_assinatura_input = request.form.get('tipo_assinatura')

        if not all([new_password, confirm_new_password, cpf_input, tipo_assinatura_input]):
            flash('Preencha todos os campos.', 'error')
            return render_template('reset_password.html', token=token, cpf_input=cpf_input, tipo_assinatura_input=tipo_assinatura_input)

        if new_password != confirm_new_password:
            flash('As novas senhas não conferem.', 'error')
            return render_template('reset_password.html', token=token, cpf_input=cpf_input, tipo_assinatura_input=tipo_assinatura_input)

        if user.cpf != cpf_input:
            flash('CPF informado não corresponde ao cadastrado.', 'error')
            return render_template('reset_password.html', token=token, cpf_input=cpf_input, tipo_assinatura_input=tipo_assinatura_input)

        if user.tipo_assinatura != tipo_assinatura_input:
            flash('Tipo de assinatura informado não corresponde ao cadastrado.', 'error')
            return render_template('reset_password.html', token=token, cpf_input=cpf_input, tipo_assinatura_input=tipo_assinatura_input)

        hashed_new_password = generate_password_hash(new_password)
        update_user_password(user.id, hashed_new_password)
        flash('Senha redefinida com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token, cpf_input="", tipo_assinatura_input="")

# Reenviar confirmação
@auth_bp.route('/reenviar-confirmacao', methods=['POST'])
def reenviar_confirmacao():
    email = request.form.get('email')
    user = get_user_by_email(email)

    if user:
        if user.confirmed:
            flash('Seu e-mail já está confirmado.', 'info')
        else:
            send_confirmation_email(user)
            flash('E-mail de confirmação reenviado!', 'success')
    else:
        flash('E-mail não encontrado.', 'warning')

    return render_template('aguarde_confirmacao.html', email=email)
