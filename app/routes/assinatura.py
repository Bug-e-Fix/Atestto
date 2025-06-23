from flask import Blueprint, render_template, request, redirect, url_for
import os

assinatura_bp = Blueprint('assinatura', __name__)

@assinatura_bp.route('/documentos')
def documentos():
    return render_template('documentos.html')

@assinatura_bp.route('/assinar', methods=['GET', 'POST'])
def assinar():
    # upload de documento
    pass
