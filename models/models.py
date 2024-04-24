from fastapi import Form, UploadFile,File
from pydantic import BaseModel

class CommentUser(BaseModel):
  idUser: int 
  comment: str

class FavoritePost(BaseModel):
  idPosts: int 
  UserId: int

class CreatePosts(BaseModel):
  picture: UploadFile = Form(...)
  title: str = Form(...)
  content: str = Form(...)
  type: str = Form()

class UpdatePost(BaseModel):
  content: str = None

class DataUser(BaseModel):
  email: str
  password:str

class allDataUser(BaseModel):
  id: int
  name: str
  lastname: str
  email: str
  post: list = None
  comments: list = None

class User(BaseModel):
  id: int
  name: str
  lastname: str
  email: str


class CreateUser(BaseModel):  
  name: str
  lastname: str
  password: str
  email:str

class UpdateUser(BaseModel):  
  name: str = None
  lastname: str = None
  email: str = None
  password: str = None
