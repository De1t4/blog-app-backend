from fastapi import APIRouter, HTTPException
from models.models import FavoritePost
from database.database import db
from models.modelsTable import favorites

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

@router.post("/favorite")
async def addFavorite(favorite: FavoritePost):
  try:
    db.connect()
    queryVerify = favorites.select().where((favorites.posts_id == favorite.idPosts) & (favorites.users_id == favorites.users_id))
    if queryVerify:
      deleteFav = favorites.update(favorite_state = "1").where((favorites.posts_id == favorite.idPosts) & (favorites.users_id == favorite.UserId))
      deleteFav.execute()
      raise HTTPException(status_code=201, detail="ADD POSTS FAVORITE")

    newFavorite = favorites.insert(posts_id = favorite.idPosts, users_id = favorite.UserId, favorite_state = 1)
    rowModify = newFavorite.execute()

    if rowModify > 0:
      raise HTTPException(status_code=201, detail="ADD POSTS FAVORITE")
    else:
      raise HTTPException(status_code=400, detail="ERROR ADD POST FAVORITE")
  finally:
    if not db.is_closed():
      db.close
  
@router.delete("/favoriteDelete/{idUser}/{idPost}")
async def deleteFavorite(idUser: int, idPost: int):
  try:
    db.connect()
    queryFav = favorites.select(favorites.favorite_state).where((favorites.posts_id == idPost) & (favorites.users_id == idUser))
    if(queryFav):
      deleteFav = favorites.update(favorite_state = "0").where((favorites.posts_id == idPost) & (favorites.users_id == idUser))
      deleteFav.execute()
      raise HTTPException(status_code=200, detail="DELETE FAVORITE POST")
  finally:
    if not db.is_closed():
      db.close()

@router.get("/favorites/{idUser}")
async def favoritesUser(idUser: int):
  try:
    db.connect()
    queryFav = favorites.select().where(favorites.users_id == idUser)

    arrLike = []
    for data in queryFav:
      if data.favorite_state == "1":
        obj_fav = {
          "favorite": data.id_like,
          "title":data.posts_id.title,
          "content":data.posts_id.content,
          "idPosts":data.posts_id.id_posts,
        }
        arrLike.append(obj_fav)

    return arrLike
  finally: 
    if not db.is_closed():
      db.close()