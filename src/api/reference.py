from fastapi import APIRouter, HTTPException
from src.api.depends import SessionDep, CurrentUserDep
from src.schemas.patent import (
    Position, Author, AuthorBase,
    RightsHolder, RightsHolderBase,
    Status, StatusBase,
    PatentType, PatentTypeBase,
    Employee, EmployeeBase
)
from src.db.crud.references import (
    get_employee, get_employees, create_employee, update_employee,
    get_author, get_authors, create_author,
    get_rights_holder, get_rights_holders, create_rights_holder,
    get_status, get_statuses, create_status,
    get_patent_type, get_patent_types, create_patent_type
)

router = APIRouter()


@router.get("/employees/", response_model=list[Employee])
async def list_employees(session: SessionDep, current_user: CurrentUserDep, skip: int = 0, limit: int = 100):
    """Get list of employees (requires authentication)"""
    employees = await get_employees(session, skip, limit)
    return employees


@router.get("/employees/{employee_id}", response_model=Employee)
async def get_employee_details(employee_id: int, session: SessionDep, current_user: CurrentUserDep):
    """Get employee details (requires authentication)"""
    employee = await get_employee(session, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.post("/employees/", response_model=Employee)
async def create_new_employee(employee: EmployeeBase, session: SessionDep):
    """Create employee"""
    db_employee = await create_employee(session, employee.dict())
    return db_employee


@router.put("/employees/{employee_id}", response_model=Employee)
async def update_employee_details(employee_id: int, employee: EmployeeBase, session: SessionDep):
    """Update employee"""
    updated_employee = await update_employee(session, employee_id, employee.dict(exclude_unset=True))
    if not updated_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return updated_employee


@router.get("/authors/", response_model=list[Author])
async def list_authors(session: SessionDep, skip: int = 0, limit: int = 100):
    """Get list of authors"""
    authors = await get_authors(session, skip, limit)
    return authors


@router.get("/authors/{author_id}", response_model=Author)
async def get_author_details(author_id: int, session: SessionDep):
    """Get author details"""
    author = await get_author(session, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.post("/authors/", response_model=Author)
async def create_new_author(author: AuthorBase, session: SessionDep):
    """Create author"""
    db_author = await create_author(session, author.dict())
    return db_author

@router.get("/rightsholders/", response_model=list[RightsHolder])
async def list_rightsholders(session: SessionDep, skip: int = 0, limit: int = 100):
    """Get list of rights holders"""
    rightsholders = await get_rights_holders(session, skip, limit)
    return rightsholders


@router.get("/rightsholders/{holder_id}", response_model=RightsHolder)
async def get_rightsholder_details(holder_id: int, session: SessionDep):
    """Get rights holder details"""
    rightsholder = await get_rights_holder(session, holder_id)
    if not rightsholder:
        raise HTTPException(status_code=404, detail="Rights holder not found")
    return rightsholder


@router.post("/rightsholders/", response_model=RightsHolder)
async def create_new_rightsholder(rightsholder: RightsHolderBase, session: SessionDep):
    """Create rights holder"""
    db_rightsholder = await create_rights_holder(session, rightsholder.dict())
    return db_rightsholder


@router.get("/statuses/", response_model=list[Status])
async def list_statuses(session: SessionDep):
    """Get list of statuses"""
    statuses = await get_statuses(session)
    return statuses


@router.get("/statuses/{status_id}", response_model=Status)
async def get_status_details(status_id: int, session: SessionDep):
    """Get status details"""
    status = await get_status(session, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status


@router.post("/statuses/", response_model=Status)
async def create_new_status(status: StatusBase, session: SessionDep):
    """Create status"""
    db_status = await create_status(session, status.dict())
    return db_status


@router.get("/types/", response_model=list[PatentType])
async def list_types(session: SessionDep):
    """Get list of patent types"""
    types = await get_patent_types(session)
    return types


@router.get("/types/{type_id}", response_model=PatentType)
async def get_type_details(type_id: int, session: SessionDep):
    """Get patent type details"""
    type_obj = await get_patent_type(session, type_id)
    if not type_obj:
        raise HTTPException(status_code=404, detail="Patent type not found")
    return type_obj


@router.post("/types/", response_model=PatentType)
async def create_new_type(type_obj: PatentTypeBase, session: SessionDep):
    """Create patent type"""
    db_type = await create_patent_type(session, type_obj.dict())
    return db_type
