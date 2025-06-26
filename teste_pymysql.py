import pymysql


host = 'localhost'
user = 'Giovanna'
password = 'Jackzera456'
database = 'SQLAtestto'

try:
    
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Conexão com o banco feita com sucesso!")

    with connection.cursor() as cursor:
        
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("Tabelas no banco:")
        for table in tables:
            print(table)

finally:
    connection.close()
    print("Conexão fechada.")
