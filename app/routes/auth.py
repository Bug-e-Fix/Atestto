from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models.user import get_user_by_email, create_user

# Blueprint SEM prefixo de URL
auth_bp = Blueprint('auth', __name__)

# Página de Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        user = get_user_by_email(email)
        if user and user.check_password(senha):
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))  # ou qualquer rota protegida
        else:
            erro = 'Credenciais inválidas'

    return render_template('login.html', erro=erro)

# Página de Logout
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Página de Registro
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not name or not email or not password or not confirm_password:
            flash('Preencha todos os campos', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('As senhas não conferem', 'error')
            return render_template('register.html')

        if get_user_by_email(email):
            flash('Email já cadastrado', 'error')
            return render_template('register.html')

        if create_user(name, email, password):
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Erro ao cadastrar usuário', 'error')

    return render_template('register.html')
