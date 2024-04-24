from database.database import db
from peewee import Model, CharField, ForeignKeyField, DateTimeField, IntegerField, AutoField

class BaseModel(Model):
  class Meta:
    database = db

class users(BaseModel):
  id_users = AutoField(primary_key=True)
  name = CharField(max_length=45)
  lastname = CharField(max_length=45)
  email = CharField(max_length=80)
  password = CharField(max_length=45)
  class Meta:
    table_name = 'users'

class friends(BaseModel):
  id_friends = AutoField(primary_key=True)
  user1_id = ForeignKeyField(users, field='id_users')
  user2_id = ForeignKeyField(users, field="id_users")
  class Meta:
    table_name = 'friends'

class typepost(BaseModel):
  id_typepost = AutoField(primary_key=True)
  TypePost = CharField(60)
  class Meta:
    table_name = 'typepost'

class posts(BaseModel):
  id_posts = AutoField(primary_key=True)
  users_id = ForeignKeyField(users, field="id_users")
  content = CharField(255)
  title = CharField(45)
  datePublication = DateTimeField()
  typepost_id = ForeignKeyField(typepost, field="id_typepost")
  imagePost = CharField(255)
  class Meta:
    table_name = 'posts'

class comments(BaseModel):
  id_comment = AutoField(primary_key=True)
  posts_id = ForeignKeyField(posts, field="id_posts")
  comment = CharField(max_length=255)
  users_id = ForeignKeyField(users, field="id_users")
  dateComment = DateTimeField()
  class Meta:
      table_name = 'comments'


class favorites(BaseModel):
  id_like = AutoField(primary_key=True)
  posts_id = ForeignKeyField(posts, field="id_posts")
  users_id = ForeignKeyField(users, field="id_users")
  favorite_state = CharField()
  class Meta:
      table_name = 'favorites'


