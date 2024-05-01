from fastapi import APIRouter, HTTPException
from database.database import db
from peewee import DoesNotExist
from models.modelsTable import friends, users

router = APIRouter( tags=["followers"])

@router.post("/addNewFollower/{idUser}/{idFollowUser}")
async def addNewFollower(idUser: int, idFollowUser: int):
  try:
      db.connect()
      # Verificar si ya existe una amistad entre los usuarios
      try:
          friends.get(user1_id=idUser, user2_id=idFollowUser)
          raise HTTPException(status_code=400, detail="THE USER IS ALREADY FOLLOWING")
      except DoesNotExist:
          # Si la amistad no existe, crear un nuevo registro
          query = friends.create(user1_id=idUser, user2_id=idFollowUser)
          if query:
              raise HTTPException(status_code=201, detail="FOLLOW SUCCESSFUL")
          else:
              raise HTTPException(status_code=500, detail="ERROR TRY AGAIN")
  finally:
      if not db.is_closed():
          db.close()

@router.delete("/deleteFollower/{idUser}/{idFollowerUser}")
async def deleteFollow(idUser: int, idFollowerUser:int):
  try:
    db.connect()
    deleteFriend = friends.delete().where((friends.user1_id == idUser) & (friends.user2_id == idFollowerUser))
    row_delete = deleteFriend.execute()
    if(row_delete > 0):
      raise HTTPException(status_code=200, detail="USER DELETE SUCCESSFUL")
    else:
      db.rollback()
      raise HTTPException(status_code=404, detail="USER NOT FOUND")

  finally:
    if not db.is_closed():
      db.close()

  
