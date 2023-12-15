from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, utils
from ..schemas import UserBase, UserResponse
from ..database import get_db

router = APIRouter(
    prefix="/users"
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserBase, db: Session = Depends(get_db)):
    # Hash a password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    created_user = models.User(**user.model_dump())
    db.add(created_user)
    db.commit()
    db.refresh(created_user)

    return created_user

@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} not found")
    return user
