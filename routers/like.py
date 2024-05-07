from fastapi import APIRouter, HTTPException
from models.models import FavoritePost
from database.database import db
from models.modelsTable import favorites, users
from peewee import DoesNotExist
router = APIRouter( tags=["like"])

@router.get("/favorite/{idPosts}/{UserId}")
async def get_favorite_state(idPosts: int, UserId: int):
  try:
    db.connect()
    queryFav = favorites.select(favorites.favorite_state).where((favorites.posts_id == idPosts) & (favorites.users_id == UserId))
    if queryFav:
      for data in queryFav:
        print(data.favorite_state)
        if(data.favorite_state == "1"):
          return {"fav": True}
        elif(data.favorite_state == "0"):
          return {"fav": False}
    return {"fav": False}

  finally:
    if not db.is_closed():
      db.close()

@router.post("/favorite/{idPosts}/{UserId}")
async def addFavorite(idPosts: int, UserId: int):
  try:
    db.connect()
    try:
      favorites.get(posts_id = idPosts, users_id = UserId)
      updateFav = favorites.update(favorite_state = "1").where((favorites.posts_id == idPosts) & (favorites.users_id == UserId))
      updateFav.execute()
      raise HTTPException(status_code=201, detail="ADD AGAIN POSTS FAVORITE")
    except DoesNotExist:
      newFavorite = favorites.create(posts_id = idPosts, users_id = UserId, favorite_state = 1)
      if(newFavorite):
        raise HTTPException(status_code=201, detail="ADD POSTS FAVORITE")
      else: 
        raise HTTPException(status_code=500, detail="ERROR TRY AGAIN")
  finally:
    if not db.is_closed():
      db.close()
  
#VERIFICAR ERRORES EN LA CONNECION DE LA BASE DE DATOS POSIBLEMENTE SEA EL EXPECT DOESNOTEXIST AGREAGADO PARA VERIFICAR
@router.delete("/favoriteDelete/{idPost}/{idUser}")
async def deleteFavorite(idPost: int, idUser: int):
  try:
    db.connect()
    try:
      users.get(id_users = idUser)
      queryFav = favorites.select(favorites.favorite_state).where((favorites.posts_id == idPost) & (favorites.users_id == idUser))
      if(queryFav):
        deleteFav = favorites.update(favorite_state = "0").where((favorites.posts_id == idPost) & (favorites.users_id == idUser))
        deleteFav.execute()
        raise HTTPException(status_code=200, detail="DELETE FAVORITE POST")
    except DoesNotExist:
      raise HTTPException(status_code=404, detail="USER NOT EXISTS")
  finally:
    if not db.is_closed():
        db.close()

@router.get("/favorites/{idUser}")
async def favoritesUser(idUser: int):
  try:
    db.connect()
    verifyUser = users.select(users.name).where(idUser == users.id_users)
    if(verifyUser):
      queryFav = favorites.select().where(favorites.users_id == idUser)
      arrLike = []
      for data in queryFav:
        if data.favorite_state == "1":
          obj_fav = {
            "favorite": data.id_like,
            "title":data.posts_id.title,
            "content":data.posts_id.content,
            "date":data.posts_id.datePublication,
            "idPosts":data.posts_id.id_posts,
          }
          arrLike.append(obj_fav)

      return arrLike
    raise HTTPException(status_code=404, detail="USER NOT EXISTS")
  finally: 
    if not db.is_closed():
      db.close()