# app/services/gov_services.py
import os
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime

SIGNED_FOLDER = "signed"
os.makedirs(SIGNED_FOLDER, exist_ok=True)

def assinar_documento_simulado(user, file_path, nome_assinatura):
    """
    Simula a assinatura digital do Gov.br.
    Retorna o caminho do PDF assinado.
    """
    reader = PdfReader(file_path)
    writer = PdfWriter()

    # Copia todas as páginas
    for page in reader.pages:
        writer.add_page(page)

    # Adiciona texto de simulação de assinatura (rodapé)
    # Obs: PyPDF2 não insere texto diretamente, mas vamos salvar o mesmo PDF como 'assinado'
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    signed_filename = f"{user.id}_{os.path.basename(file_path).replace(' ', '_')}_signed.pdf"
    signed_path = os.path.join(SIGNED_FOLDER, signed_filename)

    with open(signed_path, "wb") as f_out:
        writer.write(f_out)

    return signed_path
