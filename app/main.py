from typing import Optional, List
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, SessonLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessonLocal()
    try:
        yield db
    finally:
        db.close()


# @app.get("/sqlalchemy")
# def test_posts(db: Session = Depends(get_db)):
#     posts = db.query(models.Post).all()
#     return {"data": posts}


while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi',
                                user='postgres', password='qwer', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connecting to database failed.")
        print("Error: ", error)
        time.sleep(2)


# my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
#             {"title": "favorite food", "content": "I like pizza", "id": 2}]


# def find_post(id):
#     for p in my_posts:
#         if p["id"] == id:
#             return p


# def find_post_index(id):
#     for i, p in enumerate(my_posts):
#         print(i, p)
#         if p['id'] == id:
#             return i


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/posts", response_model=List[schemas.Post])
# pydantic 사용
# def get_posts():
#     cursor.execute("""select * from posts""")
#     posts = cursor.fetchall()
# sqlalchemy 사용
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.get("/posts/{id}", response_model=schemas.Post)
# pydantic 사용
# def get_post(id: int, response: Response):
#     cursor.execute("""select * from posts where id = %s""", (str(id),))
#     post = cursor.fetchone()
#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"post with id: {id} was not found")
# sqlalchemy 사용
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return post


@ app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
# pydantic 사용
# def create_post(post: Post):
#     cursor.execute(
#         """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) returning * """,
#         (post.title, post.content, post.published)
#     )
#     new_post = cursor.fetchone()
#     conn.commit()
# sqlalchemy 사용
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())

    # print(post)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@ app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# pydantic 사용
# def delete_post(id: int):
#     cursor.execute(
#         """delete from posts where id = %s returning *""", (str(id),))
#     deleted_post = cursor.fetchone()
#     conn.commit()
#     if deleted_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"post with id: {id} does not exist")
# sqlalchemy 사용
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@ app.put("/posts/{id}", response_model=schemas.Post)
# pydantic 사용
# def update_post(id: int, post: Post):
#     cursor.execute("""update posts set title = %s, content = %s, published = %s where id = %s returning *""",
#                    (post.title, post.content, post.published, str(id)))
#     updated_post = cursor.fetchone()
#     conn.commit()
#     if updated_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"post with id: {id} does not exist")
# sqlalchemy 사용
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if (post == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()
