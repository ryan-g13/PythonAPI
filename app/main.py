from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = False
    rating: Optional[int] = None

while True:
    try:
        conn = psycopg2.connect(database="fastapi", user="postgres", password="*********", host="localhost", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("DB Connection Succcess")
        break
    except Exception as error:
        print("DB Connection failed: ", error)
        time.sleep(3)

def get_index(id:int):
    for i, post in enumerate(my_posts):
        if id == post['id']:
            return i

@app.get("/")
def root():
    return {"message": "Hola Senor"}

@app.get("/posts")
def get_posts():
    cursor.execute("SELECT * FROM posts")
    sql_posts = cursor.fetchall()
    return {"data": sql_posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(new_post: Post):
    cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s, %s) RETURNING * """, (new_post.title, new_post.content, new_post.published, new_post.rating))
    created_post = cursor.fetchone()
    conn.commit()

    return {"data": created_post }

# Needs to be above /posts/{id} otherwise validation fails.
@app.get("/posts/latest")
def get_latest_post():
    cursor.execute("""SELECT * FROM posts ORDER BY created_at DESC""")
    latest_post = cursor.fetchone()
    print(latest_post)
    return { "data": latest_post }

@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))
    post = cursor.fetchone()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No post with ID {id} found")
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No post with ID {id} found")
    return { "status_code": status.HTTP_204_NO_CONTENT }  

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s, rating = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, post.rating, str(id),))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No post with ID {id} found")

    return { "data": updated_post }
