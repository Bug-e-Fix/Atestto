# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os
import requests
from app.services.db import get_db
from app.models.user import User

# Helpers (stubs se não tiver implementação)
try:
    from app.services.email_service import send_confirmation_email, send_reset_password_email
    from app.services.token_service import generate_token, confirm_token
except Exception:
    def send_confirmation_email(user): return False
    def send_reset_password_email(user): return False
    def generate_token(email): return ""
    def confirm_token(token, expiration=3600): return None

bp = Blueprint("auth", __name__, url_prefix="/auth")

# Config Gov.br
GOVBR_CLIENT_ID = os.getenv("GOVBR_CLIENT_ID")
GOVBR_CLIENT_SECRET = os.getenv("GOVBR_CLIENT_SECRET")
GOVBR_REDIRECT_URI = os.getenv("GOVBR_REDIRECT_URI", "http://localhost:5000/auth/callback_govbr_real")
GOVBR_AUTH_URL = "https://sso.staging.acesso.gov.br/authorize"
GOVBR_TOKEN_URL = "https://sso.staging.acesso.gov.br/token"
GOVBR_USERINFO_URL = "https://sso.staging.acesso.gov.br/userinfo"

# ----------------- LOGIN -----------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha") or request.form.get("password") or ""

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, name, email, senha, confirmed FROM usuarios WHERE email=%s", (email,))
            row = cursor.fetchone()
        finally:
            cursor.close()

        if not row:
            flash("E-mail ou senha inválidos.", "danger")
            return render_template("login.html", current_user=current_user)

        stored = row.get("senha") or ""
        password_ok = False
        try:
            if stored.startswith(("pbkdf2:", "argon2:", "scrypt:")):
                password_ok = check_password_hash(stored, senha)
            else:
                if stored == senha:
                    password_ok = True
                    try:
                        new_hash = generate_password_hash(senha)
                        ucur = conn.cursor()
                        ucur.execute("UPDATE usuarios SET senha=%s WHERE id=%s", (new_hash, row["id"]))
                        conn.commit()
                        ucur.close()
                    except Exception:
                        pass
        except Exception:
            password_ok = False

        if not password_ok:
            flash("E-mail ou senha inválidos.", "danger")
            return render_template("login.html", current_user=current_user)

        if "confirmed" in row and row.get("confirmed") in (0, "0", None):
            flash("Por favor confirme seu e-mail antes de entrar.", "warning")
            return render_template("login.html", current_user=current_user)

        user = User(id=row["id"], nome=row.get("name"), email=row["email"])
        login_user(user)
        flash("Login realizado com sucesso!", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("login.html", current_user=current_user)

# ----------------- LOGOUT -----------------
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da conta.", "info")
    return redirect(url_for("auth.login"))

# ----------------- REGISTER -----------------
@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM usuarios WHERE email=%s", (email,))
            if cursor.fetchone():
                flash("E-mail já cadastrado.", "warning")
                return redirect(url_for("auth.register"))

            hashed = generate_password_hash(senha)
            cursor.execute(
                "INSERT INTO usuarios (name, email, senha, confirmed) VALUES (%s, %s, %s, %s)",
                (nome, email, hashed, 0)
            )
            conn.commit()
            cursor.execute("SELECT id, name, email, confirmed FROM usuarios WHERE email=%s", (email,))
            user_row = cursor.fetchone()
        finally:
            cursor.close()

        try:
            send_confirmation_email(user_row)
        except Exception:
            pass

        flash("Cadastro realizado! Verifique seu e-mail para confirmar a conta.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", current_user=current_user)

# ----------------- FORGOT PASSWORD -----------------
@bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        token = generate_token(email)
        try:
            send_reset_password_email({"email": email, "token": token})
            flash("Link de recuperação enviado! Verifique seu e-mail.", "success")
        except Exception:
            flash("Erro ao enviar link de recuperação.", "danger")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html", current_user=current_user)

# ----------------- GOV.BR LOGIN -----------------
@bp.route("/login_govbr")
def login_govbr():
    """Decide se usa simulação ou fluxo real Gov.br"""
    if not GOVBR_CLIENT_ID or not GOVBR_CLIENT_SECRET:
        # Simulação
        return redirect(url_for("auth.callback_govbr", email="usuario@gov.br"))

    # Fluxo real
    auth_url = (
        f"{GOVBR_AUTH_URL}?response_type=code"
        f"&client_id={GOVBR_CLIENT_ID}"
        f"&redirect_uri={GOVBR_REDIRECT_URI}"
        f"&scope=openid+profile+email"
    )
    return redirect(auth_url)

# ----------------- CALLBACK SIMULADO -----------------
@bp.route("/callback_govbr")
def callback_govbr():
    """Callback Gov.br simulado"""
    email = request.args.get("email")
    if not email:
        flash("Falha ao autenticar com Gov.br.", "danger")
        return redirect(url_for("auth.login"))

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, email, confirmed FROM usuarios WHERE email=%s", (email,))
        user_row = cursor.fetchone()
        if not user_row:
            cursor.execute(
                "INSERT INTO usuarios (name, email, senha, confirmed) VALUES (%s,%s,%s,%s)",
                ("Usuário Gov.br", email, generate_password_hash("govbr-temporario"), 1)
            )
            conn.commit()
            cursor.execute("SELECT id, name, email, confirmed FROM usuarios WHERE email=%s", (email,))
            user_row = cursor.fetchone()
    finally:
        cursor.close()

    user = User(id=user_row["id"], nome=user_row.get("name"), email=user_row["email"])
    login_user(user)
    flash("Autenticado via Gov.br (simulado)!", "success")
    return redirect(url_for("dashboard.index"))

# ----------------- CALLBACK REAL -----------------
@bp.route("/callback_govbr_real")
def callback_govbr_real():
    """Callback Gov.br real"""
    code = request.args.get("code")
    if not code:
        flash("Erro: não recebemos o código de autenticação do Gov.br.", "danger")
        return redirect(url_for("auth.login"))

    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": GOVBR_REDIRECT_URI,
        "client_id": GOVBR_CLIENT_ID,
        "client_secret": GOVBR_CLIENT_SECRET,
    }
    token_resp = requests.post(GOVBR_TOKEN_URL, data=token_data)
    token_json = token_resp.json()
    access_token = token_json.get("access_token")

    if not access_token:
        flash("Erro ao obter token do Gov.br.", "danger")
        return redirect(url_for("auth.login"))

    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo_resp = requests.get(GOVBR_USERINFO_URL, headers=headers)
    userinfo = userinfo_resp.json()

    email = userinfo.get("email")
    nome = userinfo.get("name", "Usuário Gov.br")

    if not email:
        flash("Não foi possível obter o e-mail do Gov.br.", "danger")
        return redirect(url_for("auth.login"))

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, email, confirmed FROM usuarios WHERE email=%s", (email,))
        user_row = cursor.fetchone()
        if not user_row:
            cursor.execute(
                "INSERT INTO usuarios (name, email, senha, confirmed) VALUES (%s,%s,%s,%s)",
                (nome, email, generate_password_hash("govbr-temporario"), 1)
            )
            conn.commit()
            cursor.execute("SELECT id, name, email, confirmed FROM usuarios WHERE email=%s", (email,))
            user_row = cursor.fetchone()
    finally:
        cursor.close()

    user = User(id=user_row["id"], nome=user_row.get("name"), email=user_row["email"])
    login_user(user)
    flash("Autenticado via Gov.br (real)!", "success")
    return redirect(url_for("dashboard.index"))
