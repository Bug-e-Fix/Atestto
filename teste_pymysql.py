import pymysql

print("Tentando conectar com PyMySQL...")

try:
    conexao = pymysql.connect(
        host="localhost",
        user="root",
        password="Jackzera456",
        database="atestto",
        port=3306
    )
    print("Conexão estabelecida com sucesso via PyMySQL.")
    conexao.close()
except pymysql.MySQLError as err:
    print(f"Erro ao conectar com PyMySQL: {err}")
