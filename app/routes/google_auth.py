# app/routes/google_auth.py

from flask import redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import login_user
from app.extensions import login_manager
from app.models.user import User, get_user_by_email, create_user
import os

# Blueprint do Google
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_url="/login/google/authorized",
    scope=["profile", "email"]
)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@google_bp.route("/authorized")
def google_authorized():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")

    if not resp.ok:
        return f"Erro ao autenticar com o Google (status {resp.status_code})", 400

    data = resp.json()
    if "id" not in data or "email" not in data or "name" not in data:
        return "Erro ao obter dados do Google. Resposta incompleta.", 400

    email = data["email"]
    name = data["name"]

    user = get_user_by_email(email)

    if not user:
        user = create_user(nome=name, email=email, senha=None, google_login=True)

    login_user(user)
    return redirect(url_for("dashboard.dashboard"))
