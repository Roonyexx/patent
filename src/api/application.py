from fastapi import APIRouter, HTTPException
from src.api.depends import SessionDep, CurrentUserDep, EmployeeUserDep
from src.schemas.patent import Application, ApplicationCreate, Status
from src.db.crud.application import (
    get_application, get_applications, create_application,
    update_application, delete_application, get_applications_by_status
)

router = APIRouter()


@router.get("/", response_model=list[Application])
async def list_applications(
    session: SessionDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 100
):
    """Get list of applications (requires authentication)"""
    applications = await get_applications(session, skip, limit)
    return applications


@router.get("/{application_id}", response_model=Application)
async def get_application_details(
    application_id: int,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """Get application details by ID (requires authentication)"""
    application = await get_application(session, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.get("/status/{status_id}", response_model=list[Application])
async def get_applications_with_status(
    status_id: int,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """Get applications by status (requires authentication)"""
    applications = await get_applications_by_status(session, status_id)
    return applications


@router.post("/", response_model=Application)
async def create_new_application(
    application: ApplicationCreate,
    session: SessionDep,
    current_user: CurrentUserDep
):
    """Create new application"""
    application_data = application.dict()
    if current_user.user_type == "employee":
        application_data["employee_id"] = current_user.employee_id
    elif current_user.user_type == "author":
        application_data["author_id"] = current_user.author_id
    else:
        raise HTTPException(status_code=403, detail="Only employees or authors can create applications")

    db_application = await create_application(session, application_data)
    return db_application


@router.put("/{application_id}", response_model=Application)
async def update_application_details(
    application_id: int,
    application: ApplicationCreate,
    session: SessionDep,
    current_user: EmployeeUserDep
):
    """Update application (employees only)"""
    updated_application = await update_application(
        session, application_id, application.dict(exclude_unset=True)
    )
    if not updated_application:
        raise HTTPException(status_code=404, detail="Application not found")
    return updated_application


@router.delete("/{application_id}")
async def delete_application_by_id(
    application_id: int,
    session: SessionDep,
    current_user: EmployeeUserDep
):
    """Delete application (employees only)"""
    deleted_application = await delete_application(session, application_id)
    if not deleted_application:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application deleted"}
