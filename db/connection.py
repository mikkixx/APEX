import pymysql
import peewee

pymysql.install_as_MySQLdb()

db = peewee.MySQLDatabase(
    'apex',
    user = 'root',
    password = '',
    host = 'localhost',
    port = 3306,
    charset = 'utf8mb4'
)

def connect_db():
    try:
        db.connect(reuse_if_open=True)
        print("База данных подключена")
    except Exception as e:
        print(f"Ошибка подключения: {e}")

def close_db():
    if not db.is_closed():
        db.close()
        print("Соединение закрыто")

if __name__ == "__main__":
    print("Тестирование подключения к БД")
    connect_db()
    close_db()