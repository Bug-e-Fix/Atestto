from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = 'sua-chave-secreta-aqui'  # para sessões/flash

    # Registrar rotas
    from ..routes import auth, dashboard, assinatura
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(assinatura.bp)

    return app
