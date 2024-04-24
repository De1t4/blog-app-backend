from fastapi import APIRouter, HTTPException
from database.database import db
from models.modelsTable import friends
router = APIRouter( tags=["followers"])

@router.post("/addNewFollower/{idUser}/{idFollowUser}")
async def addNewFollower(idUser: int, idFollowUser: int):
  try:
    db.connect()
    verifyFriends = friends.select().where(friends.user1_id == idUser & friends.user2_id == idFollowUser )
    if(verifyFriends):
      raise HTTPException(status_code=400, detail="THE USER IS ALREADY FOLLOWING")
    query = friends.insert(user1_id = idUser, user2_id = idFollowUser)
    row_friend = query.execute()
    if row_friend > 0:
      raise HTTPException(status_code=201, detail="FOLLOW SUCCESSFUL")
    else:
      raise HTTPException(status_code=500, detail="ERROR TRY AGAIN")
  except Exception as e:
    raise HTTPException(status_code=500, detail={f"error: ", e})
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
      return HTTPException(status_code=200, detail="USER DELETE SUCCESSFUL")
    else:
      return HTTPException(status_code=400, detail="ERROR TRY AGAIN")
  finally:
    if not db.is_closed():
      db.close()

  
