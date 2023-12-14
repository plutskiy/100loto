from peewee import *

db_path = 'test.sqlite'
db = SqliteDatabase(db_path)

class User(Model):
    user_id = IntegerField()
    nickname = CharField()
    has_ref = BooleanField()
    joined_ref = BooleanField()

    class Meta:
        database = db

# Подключаемся к базе данных и создаем таблицы, если они еще не существуют
db.connect()
db.create_tables([User], safe=True)
User.create(user_id=1, nickname='test_user', has_ref=True, joined_ref=False)
User.create(user_id=2, nickname='another_user', has_ref=False, joined_ref=True)