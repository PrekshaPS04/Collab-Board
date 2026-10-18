from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/boards", tags=["boards"])

@router.post("/", response_model=schemas.BoardOut, status_code=201)
def create_board(
    data: schemas.BoardCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    board = models.Board(title=data.title, owner_id=current_user.id)
    db.add(board)
    db.commit()
    db.refresh(board)
    return board

@router.get("/", response_model=list[schemas.BoardOut])
def list_my_boards(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Board).filter(models.Board.owner_id == current_user.id).all()

def get_owned_board(board_id: int, db: Session, user: models.User) -> models.Board:
    board = db.get(models.Board, board_id)
    if not board or board.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.get("/{board_id}", response_model=schemas.BoardOut)
def get_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return get_owned_board(board_id, db, current_user)

@router.patch("/{board_id}", response_model=schemas.BoardOut)
def update_board(
    board_id: int,
    data: schemas.BoardUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    board = get_owned_board(board_id, db, current_user)
    if data.title is not None:
        board.title = data.title
    if data.content is not None:
        board.content = data.content
    db.commit()
    db.refresh(board)
    return board

@router.delete("/{board_id}", status_code=204)
def delete_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    board = get_owned_board(board_id, db, current_user)
    db.delete(board)
    db.commit()