from typing import List, Optional
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, oauth2
from app.schemas import PostResponse, CreatePost, PostVote
from app.database import get_db

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)

@router.get("/", response_model=List[PostVote])
# @router.get("/")
def get_posts(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user), limit:int = 10, skip:int = 0, search: Optional[str] = ""):
    # with sql vs ORM 
    # cursor.execute("SELECT * FROM posts")
    # sql_posts = cursor.fetchall()
    # sql_posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    # adding new field votes to the sql query 
    results = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return results

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(new_post: CreatePost, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # V1
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s, %s) RETURNING * """, (new_post.title, new_post.content, new_post.published, new_post.rating))
    # created_post = cursor.fetchone()
    # conn.commit()

    # V2 without unpacking dictionary
    # created_post = models.Post(title=new_post.title, content=new_post.content, published=new_post.published, rating=new_post.rating)
    created_post = models.Post(user_id = current_user.user_id, **new_post.model_dump())
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

@router.get("/{id}", response_model=PostVote)
def get_post(id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # V1 
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))
    # post = cursor.fetchone()

    post = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No post with ID {id} found")
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # V1
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    delete_query = db.query(models.Post).filter(models.Post.id == id)
    deleted_post = delete_query.first()

    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No post with ID {id} found")
    if deleted_post.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    delete_query.delete(synchronize_session=False)
    db.commit()

    return { "status_code": status.HTTP_204_NO_CONTENT }

@router.put("/{id}", response_model=PostResponse)
def update_post(id: int, post: CreatePost, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # V1
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s, rating = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, post.rating, str(id),))
    # updated_post = cursor.fetchone()
    # conn.commit()

    update_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = update_query.first()

    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No post with ID {id} found")
    if updated_post.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    update_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return update_query.first()
