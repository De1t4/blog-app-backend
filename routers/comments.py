from fastapi import APIRouter, HTTPException
from models.models import CommentUser
from database.database import db
from models.modelsTable import comments , posts
from peewee import Database

router = APIRouter( tags=["comments"])

#APIS DE LOS COMMENTS
@router.get("/getComments")
async def getComments():
  try:
    db.connect()
    response = comments.select().dicts()
    data_comments = list(response)

    return data_comments
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {str(e)}")
  finally:
    db.close()

@router.post("/createComment/{idPost}", status_code=201)
async def createComments(commentUser: CommentUser, idPost: int):
  try:
    db.connect()
    fetchData = posts.select().where(posts.id_posts == {idPost}).dicts()
    row_data = list(fetchData)
    if row_data != []:
      new_comment = comments(posts_id=idPost, comment=commentUser.comment, users_id=commentUser.idUser) 
      rows_affected = new_comment.save()
      if isinstance(db, Database) and rows_affected:
        raise HTTPException(status_code=201, detail="SUCCESFUL COMMENT CREATE")
      else:
        raise HTTPException(status_code=400, detail='COMMENT NOT CREATE')
    return HTTPException(status_code=404, detail="POST NOT EXIST")
  finally:
    db.close()


@router.delete("/deleteComment/{idComment}")
async def deleteComment(idComment: int):
  try:
    db.connect()
    deleteData = comments.delete().where(comments.id_comment == idComment)
    rows_deleted = deleteData.execute()
    if rows_deleted > 0:
      raise HTTPException(status_code=200, detail="Comentario eliminado")
    else:
      raise HTTPException(status_code=404, detail="No se encontró ningún comentario con ese ID.")
  finally:
    db.close()  