import time
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Schema of a request
class Post(BaseModel):
    title: str
    content: str
    published: bool = False
    rating: Optional[int] = None

while True:
    try:
        conn = psycopg2.connect(database="fastapi", user="postgres", password="********", host="localhost", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("DB Connection Succcess")
        break
    except Exception as error:
        print("DB Connection failed: ", error)
        time.sleep(3)

@app.get("/")
def root():
    return {"message": "Hola Senor"}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # with sql vs ORM 
    # cursor.execute("SELECT * FROM posts")
    # sql_posts = cursor.fetchall()
    sql_posts = db.query(models.Post).all()
    return {"data": sql_posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(new_post: Post, db: Session = Depends(get_db)):
    # V1
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s, %s) RETURNING * """, (new_post.title, new_post.content, new_post.published, new_post.rating))
    # created_post = cursor.fetchone()
    # conn.commit()

    # V2 without unpacking dictionary
    # created_post = models.Post(title=new_post.title, content=new_post.content, published=new_post.published, rating=new_post.rating)
    created_post = models.Post(**new_post.model_dump())
    db.add(created_post)
    db.commit()
    db.refresh(created_post)
    return {"data": created_post }

# Needs to be above /posts/{id} otherwise validation fails.
@app.get("/posts/latest")
def get_latest_post():
    cursor.execute("""SELECT * FROM posts ORDER BY created_at DESC""")
    latest_post = cursor.fetchone()
    print(latest_post)
    return { "data": latest_post }

@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # V1 
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))
    # post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No post with ID {id} found")
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # V1
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    deleted_post = db.query(models.Post).filter(models.Post.id == id)

    if deleted_post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No post with ID {id} found")
    deleted_post.delete(synchronize_session=False)
    db.commit()

    return { "status_code": status.HTTP_204_NO_CONTENT }

@app.put("/posts/{id}")
def update_post(id: int, post: Post, db: Session = Depends(get_db)):
    # V1 
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s, rating = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, post.rating, str(id),))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()

    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No post with ID {id} found")

    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return { "data": post_query.first() }
