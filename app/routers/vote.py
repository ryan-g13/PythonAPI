from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, utils
from ..schemas import Vote
from ..database import get_db
from .. import oauth2

router = APIRouter(
  prefix="/vote",
  tags=['Vote']
)

@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: Vote, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    existing_post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not existing_post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with {vote.post_id} does not exist')

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.user_id)
    found_vote = vote_query.first()
    if vote.direction == 1:
        if found_vote: 
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'{current_user.user_id} has already voted on post {vote.post_id}')
        new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.user_id)
        db.add(new_vote)
        db.commit()

        return {"message": "successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist")
        vote_query.delete(synchronize_session=False)
        db.commit()

        return {"message": "successfully removed vote"}
