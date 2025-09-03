from cryptography.fernet import Fernet
import os

def load_encrypted_env():
    # Ler a chave
    with open("secret.key", "rb") as f:
        key = f.read()
    fernet = Fernet(key)

    # Ler arquivo .env criptografado
    with open(".env.encrypted", "rb") as f:
        encrypted_data = f.read()

    # Descriptografar
    decrypted_data = fernet.decrypt(encrypted_data)

    # Salvar temporariamente em um arquivo .env para o load_dotenv
    with open(".env.temp", "wb") as f:
        f.write(decrypted_data)

    # Carregar variáveis do .env temporário
    from dotenv import load_dotenv
    load_dotenv(".env.temp")

    # Opcional: deletar o arquivo temporário depois de carregar
    os.remove(".env.temp")
