from peewee import *

db_path = 'users.sqlite'
db = SqliteDatabase(db_path)


class User(Model):
    user_id = IntegerField(primary_key=True, unique=True)
    nickname = CharField()
    tikets = IntegerField(default=0)
    archieved = BooleanField(default=False)

    class Meta:
        database = SqliteDatabase('users.sqlite')


class Tickets(Model):
    user = ForeignKeyField(User, backref='tickets', field=User.user_id)

    class Meta:
        database = SqliteDatabase('users.sqlite')


class Ref(Model):
    invite_id = ForeignKeyField(User, backref='invites', field=User.user_id, primary_key=True)
    join_id = ForeignKeyField(User, backref='joins', field=User.user_id)
    msg_count = IntegerField(default=0)

    class Meta:
        database = SqliteDatabase('users.sqlite')

def clear():
    db.connect()
    db.drop_tables([Ref, User, Tickets], safe=True)
    db.create_tables([Ref], safe=True)
    db.create_tables([Tickets], safe=True)
    db.create_tables([User], safe=True)

db.connect()
# db.drop_tables([Ref, User, Tickets], safe=True)
db.create_tables([Ref], safe=True)
db.create_tables([Tickets], safe=True)
db.create_tables([User], safe=True)
