from flask import Flask
from flask_login import LoginManager
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.assinatura import assinatura_bp
from app.models.user import get_user_by_id  # função que vamos criar no user.py

app = Flask(__name__)
app.config.from_object('config.Config')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)  # pega o usuário do banco via pymysql

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'
app.config['SIGNED_FOLDER'] = 'signed'

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(assinatura_bp)


if __name__ == '__main__':
    app.run(debug=True, port=5050) 