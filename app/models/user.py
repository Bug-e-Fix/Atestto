# app/models/user.py
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, nome, email):
        # Flask-Login espera que get_id() retorne string
        self.id = str(id)
        self.nome = nome
        self.email = email

    def get_id(self):
        return str(self.id)
