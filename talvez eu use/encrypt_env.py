from cryptography.fernet import Fernet

# Carregar a chave
with open("secret.key", "rb") as f:
    key = f.read()

fernet = Fernet(key)

# Carregar .env original
with open("env_plain.txt", "rb") as f:
    data = f.read()

# Criptografar
encrypted = fernet.encrypt(data)

# Salvar .env criptografado
with open(".env.encrypted", "wb") as f:
    f.write(encrypted)

print("Arquivo .env criptografado criado com sucesso!")
