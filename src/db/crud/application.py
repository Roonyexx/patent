from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.models import Application, Status
from datetime import datetime


async def get_application(session: AsyncSession, application_id: int):
    result = await session.execute(
        select(Application)
        .where(Application.id == application_id)
        .options(selectinload(Application.status), selectinload(Application.patent))
    )
    return result.scalars().first()


async def get_applications(session: AsyncSession, skip: int = 0, limit: int = 100):
    result = await session.execute(
        select(Application)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Application.status), selectinload(Application.patent))
    )
    return result.scalars().all()


async def get_applications_by_status(session: AsyncSession, status_id: int, skip: int = 0, limit: int = 100):
    result = await session.execute(
        select(Application)
        .where(Application.status_id == status_id)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Application.status), selectinload(Application.patent))
    )
    return result.scalars().all()


async def create_application(session: AsyncSession, application_data: dict):
    db_application = Application(
        submission_date=datetime.utcnow(),
        documents=application_data.get("documents"),
        status_id=application_data.get("status_id", 1),  # Default to 'Created' status (id=1)
        employee_id=application_data.get("employee_id"),
        author_id=application_data.get("author_id")
    )
    session.add(db_application)
    await session.commit()
    await session.refresh(db_application)
    return db_application


async def update_application(session: AsyncSession, application_id: int, update_data: dict):
    db_application = await get_application(session, application_id)
    if not db_application:
        return None
    
    for key, value in update_data.items():
        if value is not None:
            setattr(db_application, key, value)
    
    db_application.modification_date = datetime.utcnow()
    await session.commit()
    await session.refresh(db_application)
    return db_application


async def delete_application(session: AsyncSession, application_id: int):
    db_application = await get_application(session, application_id)
    if db_application:
        await session.delete(db_application)
        await session.commit()
    return db_application
