from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..schemas import TaskCreate, TaskUpdate, TaskOut
from ..services.task_service import TaskService
from ..models import StatusEnum

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

from fastapi import UploadFile, File
import tempfile, os

@router.post("/board/{board_id}/transcribe")
async def transcribe_meeting(
    board_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Загрузить аудиозапись встречи → получить задачи.
    Поддерживает .ogg, .mp3, .wav, .m4a, .mp4
    """
    from ..services.audio_service import transcribe_and_extract_tasks

    # Сохраняем во временный файл
    suffix = os.path.splitext(file.filename)[1] or ".ogg"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(await file.read())
    tmp.close()

    try:
        tasks = await transcribe_and_extract_tasks(tmp.name, board_id, db)
    finally:
        os.unlink(tmp.name)

    return {"created_tasks": tasks, "count": len(tasks)}

@router.get("/board/{board_id}", response_model=list[TaskOut])
async def get_tasks(board_id: int, db: AsyncSession = Depends(get_db)):
    return await TaskService.get_board_tasks(db, board_id)


@router.post("/board/{board_id}", response_model=TaskOut)
async def create_task(board_id: int, data: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await TaskService.create_task(db, board_id, data)


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, data: TaskUpdate, db: AsyncSession = Depends(get_db)):
    return await TaskService.update_task(db, task_id, data)


@router.patch("/{task_id}/move", response_model=TaskOut)
async def move_task(task_id: int, status: StatusEnum, db: AsyncSession = Depends(get_db)):
    return await TaskService.move_task(db, task_id, status)


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    await TaskService.delete_task(db, task_id)
    return {"ok": True}