import time
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(database="fastapi", user="postgres", password="Basstard", host="localhost", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("DB Connection Succcess")
        break
    except Exception as error:
        print("DB Connection failed: ", error)
        time.sleep(3)

app.include_router(post.router)
app.include_router(user.router)

@app.get("/")
def root():
    return {"message": "Hola Senor, Como esta?"}
