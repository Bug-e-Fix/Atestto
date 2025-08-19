from flask import Flask, redirect, url_for
from config import Config
from app.services.db import init_db
from app.extensions import login_manager, mail
from flask_login import current_user

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mail.init_app(app)

    # Inicializa LoginManager
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # Registra Blueprints
    from app.routes import auth, dashboard, assinatura, document
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(assinatura.bp)
    app.register_blueprint(document.bp)

    # Inicializa banco
    with app.app_context():
        db = init_db(app)

    # Redireciona "/" para login ou dashboard
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.dashboard_view"))
        return redirect(url_for("auth.login"))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
