# app/services/token_service.py
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def _get_serializer():
    secret = current_app.config.get("SECRET_KEY") or current_app.config.get("SECRET")
    salt = current_app.config.get("SECURITY_PASSWORD_SALT", "atestto-salt")
    return URLSafeTimedSerializer(secret, salt=salt)

def generate_token(email: str) -> str:
    s = _get_serializer()
    return s.dumps(email)

def confirm_token(token: str, expiration=3600) -> str | None:
    """
    Retorna o e-mail decodificado se token válido e dentro do tempo (segundos).
    Caso contrário retorna None.
    """
    s = _get_serializer()
    try:
        email = s.loads(token, max_age=expiration)
        return email
    except Exception:
        return None
