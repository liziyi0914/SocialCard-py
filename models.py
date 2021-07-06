from peewee import *

database = MySQLDatabase('social_card', **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': 'localhost', 'user': 'pma', 'password': 'lzy2002LZY'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Profiles(BaseModel):
    avatar = TextField()
    name = TextField()
    path = TextField()

    class Meta:
        table_name = 'profiles'

class ProfileGroups(BaseModel):
    name = TextField()
    profile = ForeignKeyField(column_name='profile_id', field='id', model=Profiles)

    class Meta:
        table_name = 'profile_groups'

class Cards(BaseModel):
    color = TextField()
    description = TextField()
    group = ForeignKeyField(column_name='group_id', field='id', model=ProfileGroups, null=True)
    icon = TextField()
    name = TextField()
    title = TextField()
    type = TextField()
    url = TextField()

    class Meta:
        table_name = 'cards'

class Logs(BaseModel):
    ip = TextField()
    path = TextField()
    time = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    tracker = TextField(null=True)
    ua = TextField()

    class Meta:
        table_name = 'logs'

class Users(BaseModel):
    name = TextField()
    pwd = TextField()
    salt = TextField()

    class Meta:
        table_name = 'users'

class Tokens(BaseModel):
    token = TextField()
    update_time = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    user = ForeignKeyField(column_name='user_id', field='id', model=Users)

    class Meta:
        table_name = 'tokens'

