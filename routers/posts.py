from fastapi import APIRouter, Form, HTTPException, UploadFile, File
from models.models import UpdatePost
from database.database import db
from models.modelsTable import posts, users, comments, favorites
import cloudinary.uploader 
from fastapi.responses import JSONResponse

router = APIRouter( tags=["posts"])

@router.get("/getPosts")
async def getPosts():
  try:
    db.connect()
    response = posts.select(posts.id_posts, posts.content, posts.title, posts.datePublication,  posts.imagePost, users.name, users.id_users, posts.typepost_id).join(users, on=(users.id_users == posts.users_id))
    arrPosts = []
    for data in response:
      obj_posts ={
          "id": data.id_posts,
          "content": data.content,
          "title": data.title,
          "datePosts": data.datePublication,
          "name":data.users_id.name,
          "idUser":data.users_id.id_users,
          "type":data.typepost_id.TypePost,
          "picture":data.imagePost if data.imagePost else "",
          "comments": []      
      }
      dataComment = comments.select(users.id_users, users.name, users.lastname, comments.dateComment, users.email, comments.comment, comments.id_comment).join(users, on=(users.id_users == comments.users_id)).where(comments.posts_id == data.id_posts)
      for comment in dataComment:
        obj_comments = {
            "idUser":comment.users_id.id_users,
            "name":comment.users_id.name,
            "lastname":comment.users_id.lastname,
            "dateComment":comment.dateComment,
            "email": comment.users_id.email,
            "content": comment.comment,
            "idComment":comment.id_comment
        }
        obj_posts["comments"].append(obj_comments)
      arrPosts.append(obj_posts)
    return arrPosts
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {str(e)}")
  finally:
    if not db.is_closed():
      db.close()


@router.get("/getPosts/{id_posts}")
async def getPosts(id_posts: int):
  try:
    db.connect()
    response = posts.select(posts.id_posts, posts.content, posts.title, posts.datePublication, posts.imagePost, users.name, users.id_users).join(users, on=(users.id_users == posts.users_id)).where(posts.id_posts == id_posts)
    if(response):
      for data in response:
        obj_posts = {
          "id": data.id_posts,
          "content": data.content,
          "title": data.title,
          "datePosts": data.datePublication,
          "name":data.users_id.name,
          "idUser":data.users_id.id_users,
          "picture":data.imagePost if data.imagePost else "",
          "comments":[]
        }
      dataComments = comments.select(users.id_users, users.name, users.lastname, comments.dateComment, users.email, comments.comment, comments.id_comment).join(users, on=(users.id_users == comments.users_id)).where(comments.posts_id == id_posts)
      for info in dataComments:
          obj_comments = {
              "idUser":info.users_id.id_users,
              "name":info.users_id.name,
              "lastname":info.users_id.lastname,
              "dateComment":info.dateComment,
              "email": info.users_id.email,
              "content": info.comment,
              "idComment":info.id_comment,          
              }
          obj_posts["comments"].append(obj_comments)
      return obj_posts
  finally:
    if not db.is_closed():
        db.close()

        
@router.get("/getPostUser/{idUser}")
async def getPostUser(idUser: int):
  try:
    db.connect()
    response = users.select().where(users.id_users == idUser)
    if(response):
      postsUser = posts.select().join(users, on=(users.id_users == posts.users_id)).where(posts.users_id == idUser)
      arrPosts = []
      for data in postsUser:
        obj_post = {
          "title":data.title,
          "id_posts":data.id_posts
        }
        arrPosts.append(obj_post)
      return arrPosts
      
    raise HTTPException(status_code=404, detail="USER NOT FOUND")
  finally:
    if not db.is_closed():
        db.close()

@router.post("/createPosts/{idUser}", status_code=201) 
async def createPost(idUser: int, Picture: UploadFile = File(...) ,Title: str = Form(...) ,Content: str = Form(...),Type: str = Form()):
  if not Picture:
    raise HTTPException(status_code=404, detail="File not found")
  try:
    db.connect()
    response = cloudinary.uploader.upload(Picture.file, folder="blog")
    responseURL = response['secure_url']

    newPosts = posts(users_id = idUser, content = Content, title = Title, typepost_id = Type, imagePost = responseURL)
    newPosts.save()
    return JSONResponse(content="POST CREATE SUCESSFUL")
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {str(e)}")
  finally:
    db.close()
  

@router.delete("/deletePost/{idPosts}")
async def deletPost(idPosts: int):
  try:
    db.connect()
    # Borramos los comentarios relacionados con el post
    queryDeleteComment = comments.delete().where(comments.posts_id == idPosts)
    rows_deleted_comment = queryDeleteComment.execute()
    # Borramos las entradas de favoritos relacionadas con el post
    queryDeleteFavorite = favorites.delete().where(favorites.posts_id == idPosts)
    rows_deleted_favorite = queryDeleteFavorite.execute()
    # Borramos el post
    queryDeletePost = posts.delete().where(posts.id_posts == idPosts)
    rows_deleted_post = queryDeletePost.execute()
    # Si se eliminaron filas en cualquiera de las tablas, se confirma la transacción y se devuelve un éxito
    if rows_deleted_comment > 0 or rows_deleted_favorite > 0 or rows_deleted_post > 0:
        raise HTTPException(status_code=200, detail="POST DELETE")
    else:
        # Si no se eliminaron filas, se revierte la transacción y se devuelve un error
        db.rollback()
        raise HTTPException(status_code=404, detail="POST NOT FOUND")
  finally:
    if not db.is_closed():
      db.close()
  

@router.put("/updatePosts/{idPosts}")
async def updateUser(idPosts: int, post: UpdatePost):
  try:
    db.connect()
    if post.content is not None:
      verifyPost = posts.select().where(posts.id_posts == idPosts)
      if(verifyPost):
        queryPost = posts.update(content = post.content).where(posts.id_posts == idPosts)
        row_affect = queryPost.execute()
        if(row_affect > 0):
          raise HTTPException(status_code=200, detail="POST MODIFY SUCESSFUL") 
      raise HTTPException(status_code=404, detail="POST NOT EXIST")
    raise HTTPException(status_code=400, detail="GET INTO NEW CONTENT COMMENT")
  finally:
    if not db.is_closed():
      db.close

