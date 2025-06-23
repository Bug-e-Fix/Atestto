from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User  # Importa o modelo User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    erro = None
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(senha):
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

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        # Verificar se usuário já existe
        if User.query.filter_by(email=email).first():
            flash('Usuário já existe')
            return redirect(url_for('auth.register'))

        novo_user = User(email=email)
        novo_user.set_password(senha)
        from app.models.user import db
        db.session.add(novo_user)
        db.session.commit()
        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('auth.login'))

    return render_template('register.html')
