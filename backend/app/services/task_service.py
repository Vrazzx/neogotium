from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sql_update
from ..models import Task, Board, StatusEnum, PriorityEnum
from ..schemas import TaskCreate, TaskUpdate, ParsedTask


class TaskService:

    @staticmethod
    async def get_board_tasks(db: AsyncSession, board_id: int) -> list[Task]:
        result = await db.execute(
            select(Task)
            .where(Task.board_id == board_id)
            .order_by(Task.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def create_task(db: AsyncSession, board_id: int, data: TaskCreate) -> Task:
        task = Task(board_id=board_id, **data.model_dump())
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def create_from_parsed(
        db: AsyncSession,
        board_id: int,
        parsed: ParsedTask,
        source_message: str = "",
    ) -> Task:
        """Создаёт задачу из результата AI-парсера."""
        task = Task(
            board_id=board_id,
            title=parsed.title,
            assignee=parsed.assignee or None,
            priority=PriorityEnum(parsed.priority),
            tag=parsed.tag,
            status=StatusEnum.todo,
            source_message=source_message,
            created_by_ai=True,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def move_task(db: AsyncSession, task_id: int, new_status: StatusEnum) -> Task:
        """Перемещение карточки между колонками."""
        await db.execute(
            sql_update(Task)
            .where(Task.id == task_id)
            .values(status=new_status)
        )
        await db.commit()
        result = await db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one()

    @staticmethod
    async def update_task(db: AsyncSession, task_id: int, data: TaskUpdate) -> Task:
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        await db.execute(
            sql_update(Task).where(Task.id == task_id).values(**update_data)
        )
        await db.commit()
        result = await db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one()

    @staticmethod
    async def delete_task(db: AsyncSession, task_id: int) -> None:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if task:
            await db.delete(task)
            await db.commit()