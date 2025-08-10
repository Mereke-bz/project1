import psycopg2

conn = psycopg2.connect(
    dbname='heavyaura',
    user='heavyaura',
    password='heavyaura',
    host='localhost',
    port='5432'
)

print("Успешное подключение к базе данных")
conn.close()
