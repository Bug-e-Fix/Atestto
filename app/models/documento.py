from app.extensions import db
from datetime import datetime

class Documento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    dados = db.Column(db.LargeBinary, nullable=False)  
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pendente')
