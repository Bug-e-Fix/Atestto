from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('documentos', __name__, url_prefix='/documentos')

@bp.route('/enviados')
@login_required
def enviados():
    return render_template('documentos_enviados.html')

@bp.route('/recebidos')
@login_required
def recebidos():
    return render_template('documentos_recebidos.html')
