from fastapi import APIRouter, HTTPException
from jose import jwt
from peewee import fn
from datetime import datetime, timedelta
from models.models import CreateUser, DataUser
from database.database import db
from models.modelsTable import users, friends, posts, comments
from passlib.context import CryptContext

router = APIRouter( tags=["users"])

SECRET_KEY = "4bca2946943ea021b6dd7e32ee4a05449c4742cc2a7c02364836dbf48bdce2bbdd7c170da4461251b4b6f6a6e723ca11026413846b9af5e788bd92f34971db18"
ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def createToken(data:dict):
  to_encode = data.copy()
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#APIS DE LOS USUARIOS
@router.post("/loginUser")
async def loginUser(data: DataUser):
  try:
    if data.email and data.password is not None:
      db.connect()
      response = users.select().where(users.email == data.email)

      if response:
        for infoUser in response:
          password = infoUser.password
        if(verify_password(data.password, password)):
          tokenData = {"sub":data.email, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}
          accessToken = createToken(tokenData)

          for data_row in response:
            obj_user = {
              "idUser": data_row.id_users,
              "name": data_row.name,
              "lastname":data_row.lastname,
              "email":data_row.email,
              "token": accessToken
            }
            
          return obj_user
        raise HTTPException(status_code=400, detail="PASSWORD INCORRECT")
      raise HTTPException(status_code=404, detail="El usuario no existe")
    raise HTTPException(status_code=400, detail="Faltan Datos")

  finally:
    if not db.is_closed():
        db.close()

@router.get("/usersData/{userId}")
async def getUsersData(userId: int):
  try:
    dataUser = []
    db.connect()
    response = users.select()
    myfollower = friends.select().where(friends.user1_id == {userId})

    for data in response:
      obj_users = {
          "id": data.id_users,
          "name": data.name,
          "lastname": data.lastname,
          "email": data.email,
          "follow": 0  # Usar el valor actual de "follow"
      }
      for follow in myfollower:
        if(data.id_users == follow.user2_id.id_users):
          obj_users["follow"] = 1  # Cambiar a 1 si se cumple la condición          
          break

      dataUser.append(obj_users)
    return dataUser
        
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {str(e)}")
  finally:
    if not db.is_closed():
        db.close()

@router.get("/users")
async def getUsers():
  try:
    db.connect()
    users_data = users.select().dicts()
    dataUsers = list(users_data)
    
    return dataUsers
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {str(e)}")
  finally:
    if not db.is_closed():
        db.close()

@router.get("/users/{user_id}")
async def getUser(user_id: int):
  try:
    db.connect()
    response = users.select().where(users.id_users == user_id)
    if(response):
      dataPosts = posts.select(posts.id_posts, posts.title, posts.content, posts.datePublication).join(users, on=(users.id_users == posts.users_id)).where(users.id_users == user_id)
      dataComments = comments.select().join(users, on=(users.id_users == user_id)).where(comments.users_id == user_id)
      dataFriends = (friends
        .select(
            fn.SUM(fn.IF(friends.user1_id == user_id, 1, 0)).alias('Follow'),
            fn.SUM(fn.IF(friends.user2_id == user_id, 1, 0)).alias('FollowMe')
        )
        .where((friends.user1_id == user_id) | (friends.user2_id == user_id)))
      for data in response:
        user_obj = {
          "id": data.id_users,
          "name": data.name,
          "lastname": data.lastname,
          "email": data.email,
          "posts": [],  # Inicializamos una lista vacía para los posts
          "comments":[],
          "follows":0,
          "followMe": 0
        }
      if(dataPosts):
        for post in dataPosts:
          post_obj ={
            "id_posts": post.id_posts,
            "title":post.title,
            "content":post.content,
            "date":post.datePublication
          }
          user_obj["posts"].append(post_obj)

      if(dataComments):
        for info in dataComments:
          comment_obj = {
            "id_comment": info.id_comment,
            "comment": info.comment,
            "dateComment": info.dateComment
          }
          user_obj["comments"].append(comment_obj)
      if dataFriends:
        for follow in dataFriends:
          user_obj["follows"] = follow.Follow if follow.Follow else 0
          user_obj["followMe"] = follow.FollowMe if follow.FollowMe else 0
      return user_obj
    raise HTTPException(status_code=404, detail="USER NOT FOUND")
  finally:
    if not db.is_closed():
        db.close()

        
@router.delete("/deleteUser/{user_id}")
async def deleteUser(user_id: int):
  try:
    db.connect()
    response = users.select().where(users.id_users == user_id)
    if(response):
      userDelete = users.delete().where(users.id_users == user_id)
      userDelete.execute()
      raise HTTPException(status_code=200, detail="USER DELETE")
    raise HTTPException(status_code=404, detail="USER NOT FOUND")
  finally:
    if not db.is_closed():
        db.close()

        
@router.post("/createUser", status_code=201) 
async def registerUser(user: CreateUser):
  try:
    db.connect()
    verifyUser = users.select().where(users.email == user.email)
    if verifyUser:
      raise HTTPException(status_code=302, detail="USER EMAIL EXISTS")
    
    hashPassword = get_password_hash(user.password)

    newUser = users(name = user.name, lastname= user.lastname,email = user.email, password= hashPassword)
    newUser.save()
    raise HTTPException(status_code=200, detail="USER CREATE SUCESSFUL")
  finally:
    if not db.is_closed():
        db.close()

# @router.put("/updateUser/{user_id}")
# async def updateUser(user_id: int, user: UpdateUser):
#   columns = []
#   val = []

#   if user.name is not None:
#     columns.append("name=%s")
#     val.append(user.name)
#   if user.lastname is not None:
#     columns.append("lastname=%s")
#     val.append(user.lastname)
#   if user.password is not None:
#     columns.append("password=%s")
#     val.append(user.password)

#   if len(columns) > 0:
#     val.append(user_id)
#     query = "UPDATE users SET " + ", ".join(columns) + " WHERE UserId = %s"
#     mycursor.execute(query, tuple(val))
#     mydb.commit()

#     if mycursor.rowcount > 0:
#         return {"message": "USER UPDATE"}
#     else:
#         raise HTTPException(status_code=304, detail="NOT MODIFIED USER")
#   else:
#       raise HTTPException(status_code=400, detail="NO FIELDS TO UPDATE")
