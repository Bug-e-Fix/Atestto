# app/services/email_service.py
from flask import current_app, url_for
from flask_mail import Message
from app.extensions import mail
from app.services.token_service import generate_token
from typing import Mapping

def _extract_email_and_name(user) -> tuple[str, str]:
    """
    Aceita user como dict (row do DB) ou objeto com atributos.
    Retorna (email, name)
    """
    if user is None:
        return ("", "")
    if isinstance(user, Mapping):
        email = user.get("email") or user.get("Email") or user.get("EMAIL", "")
        name = user.get("name") or user.get("nome") or user.get("Name") or ""
        return (email, name)
    # objeto com atributos
    email = getattr(user, "email", "") or getattr(user, "Email", "")
    name = getattr(user, "name", "") or getattr(user, "nome", "") or getattr(user, "nome_usuario", "")
    return (email, name)

def send_confirmation_email(user) -> bool:
    """
    Envia e-mail de confirmação. `user` pode ser dict (row) ou objeto com email/name.
    Usa a rota 'auth.confirm_email' (ajuste se o endpoint for diferente).
    """
    email, name = _extract_email_and_name(user)
    if not email:
        return False

    token = generate_token(email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)

    subject = current_app.config.get("CONFIRM_SUBJECT", "Confirme seu cadastro — Atestto")
    sender = current_app.config.get("MAIL_DEFAULT_SENDER", current_app.config.get("MAIL_USERNAME"))

    html = f"""
    <p>Olá {name or ''},</p>
    <p>Obrigado por se cadastrar no <strong>Atestto</strong>! Para confirmar seu e-mail clique no link abaixo:</p>
    <p><a href="{confirm_url}">Confirmar meu e-mail</a></p>
    <p>Se você não solicitou este cadastro, ignore este e-mail.</p>
    """

    try:
        msg = Message(subject=subject, sender=sender, recipients=[email], html=html)
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.exception("Erro ao enviar email de confirmação: %s", e)
        return False

def send_reset_password_email(user) -> bool:
    """
    Envia e-mail com link para redefinir senha. `user` pode ser dict (row) ou objeto.
    Usa a rota 'auth.reset_password' (ajuste se o endpoint for diferente).
    """
    email, name = _extract_email_and_name(user)
    if not email:
        return False

    token = generate_token(email)
    reset_url = url_for('auth.reset_password', token=token, _external=True)

    subject = current_app.config.get("RESET_SUBJECT", "Redefinir senha — Atestto")
    sender = current_app.config.get("MAIL_DEFAULT_SENDER", current_app.config.get("MAIL_USERNAME"))

    html = f"""
    <p>Olá {name or ''},</p>
    <p>Recebemos uma solicitação para redefinir sua senha no <strong>Atestto</strong>.</p>
    <p>Clique no link abaixo para escolher uma nova senha (o link expira em 1 hora):</p>
    <p><a href="{reset_url}">Redefinir minha senha</a></p>
    <p>Se você não solicitou, ignore este e-mail.</p>
    """

    try:
        msg = Message(subject=subject, sender=sender, recipients=[email], html=html)
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.exception("Erro ao enviar email de reset: %s", e)
        return False


penis
