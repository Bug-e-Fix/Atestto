from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('assinatura', __name__, url_prefix='/assinatura')

@bp.route('/')
@login_required
def minha_assinatura():
    return render_template('minha_assinatura.html')
