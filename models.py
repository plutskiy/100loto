from peewee import *

db_path = 'users.sqlite'
db = SqliteDatabase(db_path)

class User(Model):
    user_id = IntegerField(primary_key=True, unique=True)
    nickname = CharField()
    tikets = BooleanField(default=0)
    archieved = BooleanField(default=False)

    class Meta:
        database = SqliteDatabase('users.sqlite')

# Подключаемся к базе данных и создаем таблицы, если они еще не существуют
db.connect()
db.create_tables([User], safe = True)