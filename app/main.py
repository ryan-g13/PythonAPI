from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg
from psycopg.rows import dict_row

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = False
    rating: Optional[int] = None

my_posts = [
    {"title": "My first post!", "content": "I should probably put content here", "published": True, "id": 1},
    {"title": "I am a wizard", "content": "Harry Potter Ipsum", "published": False, "rating": 1, "id": 2},
]

# For retry you can use a while loop 
# while True: 
try:
    with psycopg.connect("dbname=fastapi user=postgres password=******** host=localhost", row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            print("DB COnnection Succcess")
            # cur.execute("SELECT * FROM posts")
            # cur.fetchone()
            # for record in cur: 
            #     print(record)
            # break
except Exception as error:
    print("DB Connection failed: ", error)

def get_index(id:int):
    for i, post in enumerate(my_posts):
        if id == post['id']:
            return i

@app.get("/")
def root():
    return {"message": "Hola Senor"}

@app.get("/posts")
def get_posts():
    cur1 = conn.cursor()
    cur1.execute("SELECT * FROM posts")
    sql_posts = cur1.fetchall()
    print(sql_posts)
    return {"data": my_posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(new_post: Post):
    post_dict = new_post.model_dump()
    post_dict["id"] = randrange(2,4000000)
    my_posts.append(post_dict)
    return {"data": post_dict}

# Needs to be above /posts/{id} otherwise validation fails.
@app.get("/posts/latest")
def get_latest_post():
    return my_posts[len(my_posts) - 1]

@app.get("/posts/{id}")
def get_post(id: int):
    for post in my_posts:
        if id == post["id"]:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No post with ID {id} found")

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    for post in my_posts:
        if id == post["id"]:
            my_posts.remove(post)
            return { "status_code": status.HTTP_204_NO_CONTENT }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No post with ID {id} found")


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = get_index(id)

    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No post with ID {id} found")

    post_dict = post.model_dump()
    post_dict["id"] = id
    my_posts[index] = post_dict

    return { "data": post_dict }
