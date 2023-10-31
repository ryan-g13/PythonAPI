from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def root():
  return {"message": "Hola Senor"}

@app.get('/posts/')
def get_posts():
  return {"data": "Posts should be here"}