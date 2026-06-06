from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Board
from ..schemas import BoardCreate, BoardOut

router = APIRouter(prefix="/api/boards", tags=["boards"])


@router.get("", response_model=list[BoardOut])
async def get_boards(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Board))
    return result.scalars().all()


@router.post("", response_model=BoardOut)
async def create_board(data: BoardCreate, db: AsyncSession = Depends(get_db)):
    board = Board(name=data.name, telegram_chat_id=data.telegram_chat_id or None)
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return board


@router.get("/{board_id}", response_model=BoardOut)
async def get_board(board_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    if not board:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Board not found")
    return board