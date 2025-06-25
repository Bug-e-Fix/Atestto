import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Jackzera456'

    
    DB_HOST = 'localhost'
    DB_USER = 'Giovanna'
    DB_PASSWORD = 'Jackzera456'
    DB_NAME = 'Atestto'

   
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

  
    UPLOAD_FOLDER = 'uploads'
    CONVERTED_FOLDER = 'converted'
    SIGNED_FOLDER = 'signed'
