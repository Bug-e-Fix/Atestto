from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.services.user_service import create_user, verify_user, get_user_by_email
from app.services.db import get_db
from app.services.email_service import send_confirmation_email
from app.services.token_service import confirm_token
from app.extensions import login_manager
from app.models.user import User
import pymysql

bp = Blueprint('auth', __name__, url_prefix='/auth')

# ----------------- LOGIN -----------------
@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        user = verify_user(email, senha)

        if user:
            if not user.confirmed:
                flash("Você precisa confirmar seu e-mail antes de entrar!")
                return redirect(url_for("auth.login"))

            login_user(user)
            return redirect(url_for("dashboard.index"))

        flash("E-mail ou senha incorretos")
    return render_template("login.html")

# ----------------- LOGOUT -----------------
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

# ----------------- USER LOADER -----------------
@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(user['id'], user['name'], user['email'], user['confirmed'])
    return None

# ----------------- REGISTRO -----------------
@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        if get_user_by_email(email):
            flash("E-mail já cadastrado!")
            return redirect(url_for("auth.register"))

        create_user(nome, email, senha)
        user = get_user_by_email(email)
        send_confirmation_email(user)

        flash("Cadastro realizado! Verifique seu e-mail para ativar sua conta.")
        return redirect(url_for("auth.login"))

    return render_template("cadastro.html")

# ----------------- CONFIRMAÇÃO DE E-MAIL -----------------
@bp.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash("Link de confirmação inválido ou expirado.")
        return redirect(url_for("auth.register"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE usuarios SET confirmed=1 WHERE email=%s", (email,))
    db.commit()
    cursor.close()

    flash("E-mail confirmado! Agora você pode fazer login.")
    return redirect(url_for("auth.login"))

# ----------------- REENVIAR CONFIRMAÇÃO -----------------
@bp.route('/resend-confirmation', methods=['GET', 'POST'])
def resend_confirmation():
    """
    Aceita GET para exibir formulário e POST para enviar e-mail.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        user = get_user_by_email(email)
        if user and not user.confirmed:
            send_confirmation_email(user)
            flash("E-mail de confirmação reenviado! Confira a lixeira ou spam.")
        else:
            flash("E-mail não encontrado ou já confirmado.")
        return redirect(url_for("auth.login"))
    
    # GET exibe formulário para reenviar e-mail
    return render_template("resend_confirmation.html")

# ----------------- ROTA DE TESTE DE E-MAIL -----------------
@bp.route('/test-email')
def test_email():
    test_user_email = "giovanna.fernandes@grupopomin.com.br"
    user = get_user_by_email(test_user_email)
    if user:
        try:
            send_confirmation_email(user)
            return "E-mail de teste enviado com sucesso!"
        except Exception as e:
            return f"Erro ao enviar e-mail de teste: {e}"
    return "Usuário de teste não encontrado."
