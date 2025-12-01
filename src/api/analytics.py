from fastapi import APIRouter
from src.api.depends import SessionDep, CurrentUserDep
from src.db.crud.analytics import (
    get_patent_statistics_by_author,
    get_patent_statistics_by_year,
    get_patent_statistics_by_type,
    get_patent_activity_report
)

router = APIRouter()


@router.get("/by-author")
async def get_statistics_by_author(session: SessionDep, current_user: CurrentUserDep):
    """Get statistics by author (requires authentication)"""
    stats = await get_patent_statistics_by_author(session)
    return {
        "type": "author_statistics",
        "data": [{"author": row[0], "patent_count": row[1]} for row in stats]
    }


@router.get("/by-year")
async def get_statistics_by_year(session: SessionDep, current_user: CurrentUserDep):
    """Get statistics by year (requires authentication)"""
    stats = await get_patent_statistics_by_year(session)
    return {
        "type": "year_statistics",
        "data": [{"year": int(row[0]) if row[0] else None, "patent_count": row[1]} for row in stats]
    }


@router.get("/by-type")
async def get_statistics_by_type(session: SessionDep, current_user: CurrentUserDep):
    """Get statistics by type (requires authentication)"""
    stats = await get_patent_statistics_by_type(session)
    return {
        "type": "type_statistics",
        "data": [{"type_id": row[0], "patent_count": row[1]} for row in stats]
    }


@router.get("/activity-report")
async def get_activity_report(session: SessionDep, current_user: CurrentUserDep):
    """Get patent activity report (requires authentication)"""
    report = await get_patent_activity_report(session)
    return report
