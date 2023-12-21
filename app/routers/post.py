from typing import List
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app import models, oauth2
from app.schemas import PostResponse, CreatePost
from app.database import get_db

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)

@router.get("/", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # with sql vs ORM 
    # cursor.execute("SELECT * FROM posts")
    # sql_posts = cursor.fetchall()
    sql_posts = db.query(models.Post).all()
    return sql_posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(new_post: CreatePost, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # V1
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s, %s) RETURNING * """, (new_post.title, new_post.content, new_post.published, new_post.rating))
    # created_post = cursor.fetchone()
    # conn.commit()

    # V2 without unpacking dictionary
    # created_post = models.Post(title=new_post.title, content=new_post.content, published=new_post.published, rating=new_post.rating)
    print(current_user)
    created_post = models.Post(**new_post.model_dump())
    db.add(created_post)
    db.commit()
    db.refresh(created_post)
    return created_post

# Needs to be above /posts/{id} otherwise validation fails.
@router.get("/latest")
def get_latest_post(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # V1
    # cursor.execute("""SELECT * FROM posts ORDER BY created_at DESC""")
    # latest_post = cursor.fetchone()
    # print(latest_post)
    latest_post = db.query(models.Post).order_by(models.Post.created_at.desc()).first()
    return latest_post

@router.get("/{id}", response_model=PostResponse)
def get_post(id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # V1 
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))
    # post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No post with ID {id} found")
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
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

@router.put("/{id}", response_model=PostResponse)
def update_post(id: int, post: CreatePost, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
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

    return post_query.first()
