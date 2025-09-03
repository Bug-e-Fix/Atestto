# main.py
import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from app.extensions import mail, login_manager
from app.services.db import close_db, get_db
from app.models.user import User

# blueprints (ajuste se seus arquivos tiverem nomes diferentes)
from app.routes.auth import bp as auth_bp
from app.routes.dashboard import bp as dashboard_bp

# optional other blueprint
try:
    from app.routes.documentos import bp as documentos_bp
except Exception:
    documentos_bp = None

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.secret_key = os.getenv("SECRET_KEY") or "dev-secret"
    app.config["DB_HOST"] = os.getenv("DB_HOST", "localhost")
    app.config["DB_USER"] = os.getenv("DB_USER", "root")
    app.config["DB_PASSWORD"] = os.getenv("DB_PASSWORD", "")
    app.config["DB_NAME"] = os.getenv("DB_NAME", "")
    app.config["DB_PORT"] = int(os.getenv("DB_PORT", 3306))

    # mail config (optional)
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "False").lower() in ("true", "1")
    app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL", "False").lower() in ("true", "1")

    # init extensions
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # teardown db
    app.teardown_appcontext(close_db)

    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    if documentos_bp is not None:
        app.register_blueprint(documentos_bp)

    # helper available in templates to avoid BuildError while debugging
    @app.context_processor
    def utility_processor():
        def endpoint_exists(name):
            try:
                return name in (app.url_map._rules_by_endpoint.keys() if hasattr(app.url_map, "_rules_by_endpoint") else [])
            except Exception:
                return False
        return dict(endpoint_exists=endpoint_exists)

    # index redirect to login/dashboard
    @app.route("/")
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))
        return redirect(url_for("auth.login"))

    # user_loader
    @login_manager.user_loader
    def load_user(user_id):
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, name, email FROM usuarios WHERE id=%s", (user_id,))
            row = cursor.fetchone()
        finally:
            cursor.close()
        if row:
            return User(id=row["id"], nome=row.get("name"), email=row["email"])
        return None

    return app

if __name__ == "__main__":
    app = create_app()
    import logging
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug("=== Registered routes ===")
    for r in app.url_map.iter_rules():
        app.logger.debug(f"{r.endpoint} -> {r}")
    app.run(debug=True, port=5001)
