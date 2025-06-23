import pymysql

print("Script carregado! Isso confirma que o Python está rodando o arquivo.")

def main():
    print("Entrando na função main...")

    try:
        print("Tentando conectar ao banco com PyMySQL...")
        conexao = pymysql.connect(
            host="localhost",
            user="root",
            password="Jackzera456",
            database="atestto",
            port=3306
        )
        print("Conexão bem-sucedida!")

        cursor = conexao.cursor()

        cursor.execute("SHOW TABLES")
        tabelas = cursor.fetchall()
        print("Tabelas encontradas:")
        for tabela in tabelas:
            print(f"- {tabela[0]}")

        cursor.execute("SELECT * FROM usuario")
        resultado = cursor.fetchall()

        print(f"\nTotal de registros na tabela 'usuario': {len(resultado)}")
        for linha in resultado:
            print(linha)

    except pymysql.MySQLError as err:
        print(f"Erro ao acessar o banco de dados: {err}")

    finally:
        try:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()
        except:
            print("Erro ao fechar conexão.")

if __name__ == "__main__":
    print("Executando como script principal...")
    main()
