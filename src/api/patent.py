from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.api.depends import SessionDep, CurrentUserDep
from src.schemas.patent import Patent, PatentBase
from src.db.crud.patent import (
    get_patent, get_patents, create_patent,
    update_patent, delete_patent, get_expired_patents,
    get_patents_by_owner
)

router = APIRouter()


@router.get("/", response_model=list[Patent])
async def list_patents(
    session: SessionDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 100
):
    """Get list of patents (requires authentication)"""
    patents = await get_patents(session, skip, limit)
    return patents


@router.get("/expired", response_class=JSONResponse)
async def get_expired(
    session: SessionDep,
    current_user: CurrentUserDep
):
    """Get list of expired patents (requires authentication)"""
    expired_patents = await get_expired_patents(session)

    def _serialize(patent_obj):
        status = None
        if getattr(patent_obj, "status", None) is not None:
            try:
                status = {"id": patent_obj.status.id, "name": patent_obj.status.name}
            except Exception:
                status = None

        return {
            "id": patent_obj.id,
            "title": patent_obj.title,
            "issue_date": patent_obj.issue_date,
            "description": patent_obj.description,
            "rights_holder_id": patent_obj.rights_holder_id,
            "patent_type_id": patent_obj.patent_type_id,
            "application_id": patent_obj.application_id,
            "expiration_date": patent_obj.expiration_date,
            "status_id": patent_obj.status_id,
            "status": status,
        }

    return [_serialize(p) for p in expired_patents]


@router.get("/{patent_id}", response_model=Patent)
async def get_patent_details(
    patent_id: int,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """Get patent details by ID (requires authentication)"""
    patent = await get_patent(session, patent_id)
    if not patent:
        raise HTTPException(status_code=404, detail="Patent not found")
    return patent


@router.post("/", response_model=Patent)
async def create_new_patent(
    patent: PatentBase,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """Create new patent (requires authentication)"""
    patent_data = patent.dict()
    db_patent = await create_patent(session, patent_data)
    return db_patent


@router.put("/{patent_id}", response_model=Patent)
async def update_patent_details(
    patent_id: int,
    patent: PatentBase,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """Update patent (requires authentication)"""
    updated_patent = await update_patent(session, patent_id, patent.dict(exclude_unset=True))
    if not updated_patent:
        raise HTTPException(status_code=404, detail="Patent not found")
    return updated_patent


@router.delete("/{patent_id}")
async def delete_patent_by_id(
    patent_id: int,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """Delete patent (requires authentication)"""
    deleted_patent = await delete_patent(session, patent_id)
    if not deleted_patent:
        raise HTTPException(status_code=404, detail="Patent not found")
    return {"message": "Patent deleted"}
