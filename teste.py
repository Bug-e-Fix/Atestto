import mysql.connector
from mysql.connector import Error

print("Começando o script")

try:
    print("Tentando conectar")
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Jackzera456",
        database="atestto",
        connection_timeout=5  
    )
    print("Conectado com sucesso!")
    conexao.close()
except Error as err:
    print(f"Erro na conexão: {err}")

print("Fim do script.")

