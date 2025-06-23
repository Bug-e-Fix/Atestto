import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua_chave_super_secreta'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://Giovanna:Jackzera456@localhost/SQLAtestto'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pastas de arquivos
    UPLOAD_FOLDER = 'uploads'
    CONVERTED_FOLDER = 'converted'
    SIGNED_FOLDER = 'signed'
