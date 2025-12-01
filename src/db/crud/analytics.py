from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.models.models import Patent, Author, PatentAuthor, Application
from datetime import date, datetime


async def get_patent_statistics_by_author(session: AsyncSession):
    result = await session.execute(
        select(
            Author.full_name,
            func.count(Patent.id).label("patent_count")
        )
        .select_from(Author)
        .join(Application, Application.author_id == Author.id)
        .join(Patent, Patent.application_id == Application.id)
        .group_by(Author.full_name)
    )
    return result.all()


async def get_patent_statistics_by_year(session: AsyncSession):
    result = await session.execute(
        select(
            func.extract('year', Patent.issue_date).label("year"),
            func.count(Patent.id).label("patent_count")
        )
        .where(Patent.issue_date.isnot(None))
        .group_by(func.extract('year', Patent.issue_date))
    )
    return result.all()


async def get_patent_statistics_by_type(session: AsyncSession):
    result = await session.execute(
        select(
            Patent.patent_type_id,
            func.count(Patent.id).label("patent_count")
        )
        .group_by(Patent.patent_type_id)
    )
    return result.all()


async def get_patent_activity_report(session: AsyncSession):
    today = date.today()
    
    result = await session.execute(
        select(
            func.count(Patent.id).label("total_patents"),
            func.count(Patent.application_id).label("applications"),
        )
    )
    
    stats = result.first()
    
    expired_result = await session.execute(
        select(func.count(Patent.id)).where(Patent.expiration_date < today)
    )
    expired_count = expired_result.scalar()
    
    return {
        "total_patents": stats[0] or 0,
        "total_applications": stats[1] or 0,
        "expired_patents": expired_count or 0
    }


async def get_processing_time_statistics(session: AsyncSession):
    result = await session.execute(
        select(
            func.count().label("total_applications"),
        )
    )
    return result.all()
