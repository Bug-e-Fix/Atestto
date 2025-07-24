from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from app.services.document_service import (
    get_documentos_enviados,
    get_documentos_recebidos,
    get_documento_por_id,
    salvar_destinatarios_e_assinatura
)
from app.services.assinatura_service import salvar_assinatura_usuario, get_assinatura_usuario
from app.services.database import get_connection
from collections import namedtuple
from io import BytesIO
import fitz  # PyMuPDF
import base64

dashboard_bp = Blueprint('dashboard', __name__)

# Usuário fictício para testes (mantenha esse id consistente com o banco!)
UsuarioFicticio = namedtuple('UsuarioFicticio', ['id', 'name', 'email'])
usuario_ficticio = UsuarioFicticio(id=1, name='Usuário Teste', email='teste@exemplo.com')


def pdf_primeira_pagina_como_imagem_base64(dados_pdf_bytes):
    pdf = fitz.open(stream=dados_pdf_bytes, filetype="pdf")
    pagina = pdf[0]
    pix = pagina.get_pixmap()
    img_bytes = pix.tobytes("png")
    pdf.close()

    base64_img = base64.b64encode(img_bytes).decode("utf-8")
    return base64_img


@dashboard_bp.route('/dashboard')
def dashboard():
    documentos = get_documentos_enviados(usuario_ficticio.id)
    return render_template('dashboard.html', documentos=documentos, current_user=usuario_ficticio)


@dashboard_bp.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    file = request.files.get('document')
    if file and file.filename.endswith('.pdf'):
        dados = file.read()
        query = """
            INSERT INTO documentos (id_usuario, titulo, dados, data_upload, status)
            VALUES (%s, %s, %s, NOW(), 'Pendente')
        """
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (usuario_ficticio.id, file.filename, dados))
                conn.commit()
            with conn.cursor() as cursor:
                cursor.execute("SELECT LAST_INSERT_ID() as id")
                novo_doc = cursor.fetchone()
        flash('Documento enviado com sucesso!', 'success')
        return redirect(url_for('dashboard.configurar_assinatura', doc_id=novo_doc['id']))
    else:
        flash('Envie um arquivo PDF válido.', 'danger')
        return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/visualizar/<int:doc_id>')
def visualizar_documento(doc_id):
    query = "SELECT titulo, dados FROM documentos WHERE id = %s"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (doc_id,))
            doc = cursor.fetchone()
            if doc:
                return send_file(BytesIO(doc['dados']), mimetype='application/pdf',
                                 as_attachment=False, download_name=doc['titulo'])
            else:
                flash('Documento não encontrado.', 'warning')
                return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/assinar/<int:doc_id>', methods=['POST'])
def assinar_documento(doc_id):
    pos_x = int(request.form.get('pos_x', 100))
    pos_y = int(request.form.get('pos_y', 100))

    query = "SELECT dados, titulo FROM documentos WHERE id = %s"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (doc_id,))
            doc = cursor.fetchone()

    if not doc:
        flash('Documento não encontrado.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    # Inserir assinatura no PDF
    pdf_stream = BytesIO(doc['dados'])
    pdf = fitz.open(stream=pdf_stream, filetype="pdf")
    page = pdf[0]
    assinatura_texto = f"Assinado por {usuario_ficticio.name}"
    page.insert_text((pos_x, pos_y), assinatura_texto, fontsize=12)

    signed_pdf = BytesIO()
    pdf.save(signed_pdf)
    pdf.close()

    # Atualizar documento no banco
    query_update = "UPDATE documentos SET dados = %s, status = 'Assinado' WHERE id = %s"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query_update, (signed_pdf.getvalue(), doc_id))
            conn.commit()

    flash('Documento assinado com sucesso!', 'success')
    return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/documentos-enviados')
def documentos_enviados():
    documentos = get_documentos_enviados(usuario_ficticio.id)
    return render_template('documentos_enviados.html', documentos=documentos, current_user=usuario_ficticio)


@dashboard_bp.route('/documentos-recebidos')
def documentos_recebidos():
    documentos = get_documentos_recebidos(usuario_ficticio.email)
    return render_template('documentos_recebidos.html', documentos=documentos, current_user=usuario_ficticio)


@dashboard_bp.route('/minha-assinatura', methods=['GET', 'POST'])
def minha_assinatura():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        fonte = request.form.get('fonte', '').strip()
        cpf = request.form.get('cpf', '').strip()

        partes = nome.split()
        rubrica = ''
        if len(partes) >= 2:
            rubrica = partes[0][0].upper() + partes[-1][0].upper()

        salvar_assinatura_usuario(usuario_ficticio.id, nome, fonte, rubrica, cpf)
        flash('Assinatura salva com sucesso!', 'success')
        return redirect(url_for('dashboard.minha_assinatura'))

    dados = get_assinatura_usuario(usuario_ficticio.id)
    return render_template('minha_assinatura.html', dados=dados, current_user=usuario_ficticio)


@dashboard_bp.route('/configurar-assinatura/<int:doc_id>', methods=['GET', 'POST'])
def configurar_assinatura(doc_id):
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON inválido'}), 400

        destinatarios = data.get('destinatarios')
        posicoes = data.get('posicoes')

        if not destinatarios or not posicoes or len(destinatarios) != len(posicoes):
            return jsonify({'error': 'Destinatários e posições inválidos ou de tamanhos diferentes'}), 400

        try:
            salvar_destinatarios_e_assinatura(doc_id, destinatarios, posicoes)
            return jsonify({'redirect': url_for('dashboard.dashboard')})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    documento = get_documento_por_id(doc_id)
    if not documento:
        flash('Documento não encontrado.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    img_base64 = pdf_primeira_pagina_como_imagem_base64(documento['dados'])

    return render_template('configurar_assinatura.html', doc_id=doc_id, pdf_img_base64=img_base64)
