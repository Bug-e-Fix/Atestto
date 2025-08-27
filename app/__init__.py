import pymysql
from flask import Flask

# objeto global da conexão
mysql = None

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'chave_secreta_aqui'

    # Config do MySQL
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'tua_senha'
    app.config['MYSQL_DB'] = 'atestto'

    # cria conexão global
    global mysql
    mysql = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

    # importar e registrar rotas
    from app.routes import auth, dashboard, assinatura, documentos
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(dashboard.dashboard_bp)
    app.register_blueprint(assinatura.assinatura_bp)
    app.register_blueprint(documentos.documentos_bp)

    return app
