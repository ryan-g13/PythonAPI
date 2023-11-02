from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Post(BaseModel):
  title: str
  content: str
  published: bool = False
  rating: Optional[int] = None

@app.get('/')
def root():
  return {"message": "Hola Senor"}

@app.get('/posts')
def get_posts():
  return {"data": "Posts should be here"}

@app.post('/posts')
def create_post(new_post: Post):
  # title = new_post["title"]
  # data = new_post["content"]
  print(new_post.rating)
  # return {"title": title, "data": data}
  return {"Message": 'great success'}