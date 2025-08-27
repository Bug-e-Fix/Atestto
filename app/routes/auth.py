# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import pymysql.cursors

from app.services.db import get_db
from app.models.user import User

# helpers (stubs se não existir implementação)
try:
    from app.services.email_service import send_confirmation_email, send_reset_password_email
    from app.services.token_service import generate_token, confirm_token
except Exception:
    def send_confirmation_email(user): return False
    def send_reset_password_email(user): return False
    def generate_token(email): return ""
    def confirm_token(token, expiration=3600): return None

bp = Blueprint("auth", __name__, url_prefix="/auth")


# ----------------- LOGIN -----------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha") or request.form.get("password") or ""

        conn = get_db()
        cursor = conn.cursor()  # já é DictCursor pela connection
        try:
            cursor.execute("SELECT id, name, email, senha, confirmed FROM usuarios WHERE email=%s", (email,))
            row = cursor.fetchone()
        finally:
            cursor.close()

        if not row:
            flash("E-mail ou senha inválidos.", "danger")
            return render_template("login.html", current_user=current_user)

        stored = row.get("senha") or ""

        # verifica hash ou plain-text (fallback) e faz upgrade se necessário
        password_ok = False
        try:
            if stored.startswith("pbkdf2:") or stored.startswith("argon2:") or stored.startswith("scrypt:"):
                password_ok = check_password_hash(stored, senha)
            else:
                # fallback: senha em plain-text (temporário)
                if stored == senha:
                    password_ok = True
                    # tenta atualizar para hash (não fatal)
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

        # se usar campo de confirmação
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


# ----------------- RESEND CONFIRMATION -----------------
@bp.route("/resend_confirmation", methods=["GET", "POST"])
def resend_confirmation():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, name, email, confirmed FROM usuarios WHERE email=%s", (email,))
            user_row = cursor.fetchone()
        finally:
            cursor.close()

        if user_row and not user_row.get("confirmed"):
            send_confirmation_email(user_row)
            flash("E-mail de confirmação reenviado (verifique spam).", "success")
        else:
            flash("E-mail não encontrado ou já confirmado.", "warning")
        return redirect(url_for("auth.login"))

    return render_template("resend_confirmation.html", current_user=current_user)


# ----------------- FORGOT / RESET -----------------
@bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, name, email FROM usuarios WHERE email=%s", (email,))
            user_row = cursor.fetchone()
        finally:
            cursor.close()

        if user_row:
            send_reset_password_email(user_row)

        flash("Se o e-mail estiver cadastrado, enviamos instruções para redefinir a senha.", "info")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html", current_user=current_user)


@bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    email = confirm_token(token)
    if not email:
        flash("Link inválido ou expirado.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        senha = request.form.get("senha", "")
        confirmar = request.form.get("confirmar_senha", "")
        if senha != confirmar:
            flash("As senhas não conferem.", "danger")
            return render_template("reset_password.html", token=token, current_user=current_user)

        hashed = generate_password_hash(senha)
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE usuarios SET senha=%s WHERE email=%s", (hashed, email))
            conn.commit()
        finally:
            cursor.close()

        flash("Senha alterada com sucesso. Faça login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token, current_user=current_user)


# ----------------- CONFIRM -----------------
@bp.route("/confirm/<token>")
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash("Link inválido ou expirado.", "danger")
        return redirect(url_for("auth.register"))

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE usuarios SET confirmed=1 WHERE email=%s", (email,))
        conn.commit()
    finally:
        cursor.close()

    flash("E-mail confirmado! Agora você pode entrar.", "success")
    return redirect(url_for("auth.login"))


# ----------------- GOV.BR SIM -----------------
@bp.route("/login_govbr")
def login_govbr():
    return redirect(url_for("auth.callback_govbr", email="usuario@gov.br"))


@bp.route("/callback_govbr")
def callback_govbr():
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
    flash("Autenticado via Gov.br!", "success")
    return redirect(url_for("dashboard.index"))
