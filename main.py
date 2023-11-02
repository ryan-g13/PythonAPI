from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from random import randrange

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

@app.get("/")
def root():
    return {"message": "Hola Senor"}

@app.get("/posts")
def get_posts():
    return {"data": my_posts}

@app.post("/posts")
def create_post(new_post: Post):
    post_dict = new_post.model_dump()
    post_dict["id"] = randrange(2,4000000)
    my_posts.append(post_dict)
    return {"data": post_dict}

@app.get("/posts/{id}")
def get_post(id):
    for post in my_posts:
        if int(id) == post["id"]:
            return post
    return {"message": f"No post with ID {id} found"}
