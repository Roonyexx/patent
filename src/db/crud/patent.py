from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from src.models.models import Patent
from datetime import datetime, date, timedelta


async def get_patent(session: AsyncSession, patent_id: int):
    result = await session.execute(
        select(Patent)
        .where(Patent.id == patent_id)
        .options(selectinload(Patent.status))
    )
    return result.scalars().first()


async def get_patents(session: AsyncSession, skip: int = 0, limit: int = 100):
    result = await session.execute(
        select(Patent)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Patent.status))
    )
    return result.scalars().all()


async def get_expired_patents(session: AsyncSession):
    today = date.today()
    result = await session.execute(
        select(Patent)
        .where(Patent.expiration_date < today)
        .options(selectinload(Patent.status))
    )
    return result.scalars().all()


async def get_patents_by_owner(session: AsyncSession, owner_id: int):
    result = await session.execute(
        select(Patent)
        .where(Patent.rights_holder_id == owner_id)
        .options(selectinload(Patent.status))
    )
    return result.scalars().all()


async def create_patent(session: AsyncSession, patent_data: dict):
    today = date.today()
    expiration_date = today + timedelta(days=365)
    
    db_patent = Patent(
        title=patent_data.get("title"),
        issue_date=patent_data.get("issue_date", today),
        expiration_date=expiration_date,  
        description=patent_data.get("description"),
        rights_holder_id=patent_data.get("rights_holder_id"),
        patent_type_id=patent_data.get("patent_type_id"),
        status_id=patent_data.get("status_id", 1),  
        application_id=patent_data.get("application_id")
    )
    session.add(db_patent)
    await session.commit()
    await session.refresh(db_patent, ["status"])
    return db_patent


async def update_patent(session: AsyncSession, patent_id: int, update_data: dict):
    db_patent = await get_patent(session, patent_id)
    if not db_patent:
        return None
    
    for key, value in update_data.items():
        if value is not None:
            setattr(db_patent, key, value)
    
    await session.commit()
    await session.refresh(db_patent)
    return db_patent


async def delete_patent(session: AsyncSession, patent_id: int):
    db_patent = await get_patent(session, patent_id)
    if db_patent:
        await session.delete(db_patent)
        await session.commit()
    return db_patent
