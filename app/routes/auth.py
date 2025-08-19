from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, UserMixin
from app.services.user_service import create_user, verify_user, get_user_by_email
from app.services.db import get_db
from app.services.email_service import send_confirmation_email
from app.services.token_service import confirm_token
from app.extensions import login_manager

bp = Blueprint('auth', __name__, url_prefix='/auth')


# ----------------- CLASSE USER -----------------
class User(UserMixin):
    def __init__(self, id, nome, email):
        self.id = id
        self.nome = nome
        self.email = email


# ----------------- LOGIN -----------------
@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        user_data = verify_user(email, senha)
        if user_data:
            if not user_data['confirmed']:
                flash("Você precisa confirmar seu e-mail antes de entrar!")
                return redirect(url_for("auth.login"))

            user = User(user_data['id'], user_data['name'], user_data['email'])
            login_user(user)
            return redirect(url_for("dashboard.dashboard_view"))

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
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(user['id'], user['name'], user['email'])
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

        create_user(nome, email, senha)  # senha já criptografada
        send_confirmation_email(email)   # envia e-mail de confirmação automaticamente

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
@bp.route('/resend-confirmation', methods=['POST'])
def resend_confirmation():
    email = request.form.get('email')
    user = get_user_by_email(email)
    if user and not user['confirmed']:
        send_confirmation_email(email)  # reenviar e-mail automaticamente
        flash("E-mail de confirmação reenviado! Confira a lixeira ou spam.")
    else:
        flash("E-mail não encontrado ou já confirmado.")
    return redirect(url_for("auth.login"))


# ----------------- ROTA DE TESTE DE E-MAIL -----------------
@bp.route('/test-email')
def test_email():
    test_user_email = "giovanna.fernandes@grupopomin.com.br"  # coloque aqui um e-mail válido
    try:
        send_confirmation_email(test_user_email)
        return "E-mail de teste enviado com sucesso!"
    except Exception as e:
        return f"Erro ao enviar e-mail de teste: {e}"
