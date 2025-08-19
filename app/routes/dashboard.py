from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route("/")
@login_required
def dashboard_view():
    return render_template("dashboard.html", nome=current_user.nome)
