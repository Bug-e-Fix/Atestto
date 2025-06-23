from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.assinatura import assinatura_bp
from app.models.user import db, User

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Inicializa extensões
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Configura pastas
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'
app.config['SIGNED_FOLDER'] = 'signed'

# Registra os Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(assinatura_bp)

# Cria as tabelas do banco
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5050)