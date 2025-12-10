from typing import Optional
from fastapi import APIRouter, HTTPException
from src.api.depends import SessionDep, CurrentUserDep, EmployeeUserDep
from src.schemas.patent import (
    Position, Author, AuthorBase, AuthorDetailed,
    RightsHolder, RightsHolderBase,
    Status, StatusBase,
    PatentType, PatentTypeBase,
    Employee, EmployeeBase,
    Passport, PassportBase,
    PatentBrief, Application as ApplicationSchema
)
from src.db.crud.references import (
    get_employee, get_employees, create_employee, update_employee, delete_employee,
    get_author, get_authors, create_author, update_author, delete_author,
    get_passport, get_passports, create_passport, update_passport, delete_passport,
    get_rights_holder, get_rights_holders, create_rights_holder,
    get_status, get_statuses, create_status,
    get_patent_type, get_patent_types, create_patent_type,
    get_positions
)
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.models import Author as AuthorModel, Application, Patent, PatentAuthor

router = APIRouter(prefix="/reference", tags=["reference"])


@router.get("/employees/", response_model=list[Employee])
async def list_employees(
        session: SessionDep,
        current_user: CurrentUserDep,
        full_name: Optional[str] = None,
        passport_series: Optional[int] = None,
        passport_number: Optional[int] = None,
        position_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
):
    """Получить список сотрудников с фильтрацией"""
    employees = await get_employees(
        session=session,
        full_name=full_name,
        passport_series=passport_series,
        passport_number=passport_number,
        position_id=position_id,
        skip=skip,
        limit=limit
    )
    return employees


@router.get("/employees/{employee_id}", response_model=Employee)
async def get_employee_details(
        employee_id: int,
        session: SessionDep,
        current_user: CurrentUserDep
):
    """Получить информацию о сотруднике по ID"""
    employee = await get_employee(session, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.post("/employees/", response_model=Employee)
async def create_new_employee(
        employee: EmployeeBase,
        session: SessionDep,
        current_user: EmployeeUserDep  # Только сотрудники могут создавать новых сотрудников
):
    """Создать нового сотрудника"""
    db_employee = await create_employee(session, employee.dict())
    return db_employee


@router.put("/employees/{employee_id}", response_model=Employee)
async def update_employee_details(
        employee_id: int,
        employee: EmployeeBase,
        session: SessionDep,
        current_user: CurrentUserDep  # Все авторизованные могут редактировать
):
    """Обновить информацию о сотруднике"""
    updated_employee = await update_employee(
        session, employee_id, employee.dict(exclude_unset=True)
    )
    if not updated_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return updated_employee


@router.delete("/employees/{employee_id}")
async def delete_employee_by_id(
        employee_id: int,
        session: SessionDep,
        current_user: CurrentUserDep  # Все авторизованные могут удалять
):
    """Удалить сотрудника"""
    deleted_employee = await delete_employee(session, employee_id)
    if not deleted_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}


@router.get("/authors/", response_model=list[Author])
async def list_authors(
        session: SessionDep,
        current_user: CurrentUserDep,
        full_name: Optional[str] = None,
        passport_series: Optional[int] = None,
        passport_number: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
):
    """Получить список авторов с фильтрацией"""
    authors = await get_authors(
        session=session,
        full_name=full_name,
        passport_series=passport_series,
        passport_number=passport_number,
        skip=skip,
        limit=limit
    )
    return authors


@router.get("/authors/{author_id}", response_model=AuthorDetailed)
async def get_author_details(
        author_id: int,
        session: SessionDep,
        current_user: CurrentUserDep
):
    """Получить детальную информацию об авторе"""
    result = await session.execute(
        select(AuthorModel)
        .where(AuthorModel.id == author_id)
        .options(
            selectinload(AuthorModel.passport),
            selectinload(AuthorModel.patent_authors).selectinload(PatentAuthor.patent)
        )
    )
    author = result.scalars().first()

    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    # Get applications for this author
    apps_result = await session.execute(
        select(Application)
        .where(Application.author_id == author_id)
        .options(selectinload(Application.status), selectinload(Application.patent))
    )
    applications = apps_result.scalars().all()

    # Get patents from patent_authors association
    patents = [pa.patent for pa in author.patent_authors] if author.patent_authors else []

    author_dict = AuthorDetailed.from_orm(author).__dict__
    author_dict['applications'] = [ApplicationSchema.from_orm(app) for app in applications]
    author_dict['patents'] = [PatentBrief.from_orm(p) for p in patents]

    return AuthorDetailed(**author_dict)


@router.post("/authors/", response_model=Author)
async def create_new_author(
        author: AuthorBase,
        session: SessionDep,
        current_user: CurrentUserDep
):
    """Создать нового автора"""
    db_author = await create_author(session, author.dict())
    return db_author


@router.put("/authors/{author_id}", response_model=Author)
async def update_author_details(
        author_id: int,
        author: AuthorBase,
        session: SessionDep,
        current_user: CurrentUserDep  # Все авторизованные могут редактировать
):
    """Обновить информацию об авторе"""
    updated_author = await update_author(
        session, author_id, author.dict(exclude_unset=True)
    )
    if not updated_author:
        raise HTTPException(status_code=404, detail="Author not found")
    return updated_author


@router.delete("/authors/{author_id}")
async def delete_author_by_id(
        author_id: int,
        session: SessionDep,
        current_user: CurrentUserDep  # Все авторизованные могут удалять
):
    """Удалить автора"""
    deleted_author = await delete_author(session, author_id)
    if not deleted_author:
        raise HTTPException(status_code=404, detail="Author not found")
    return {"message": "Author deleted successfully"}


@router.get("/passports/", response_model=list[Passport])
async def list_passports(
        session: SessionDep,
        skip: int = 0,
        limit: int = 100
):
    """Получить список паспортов"""
    passports = await get_passports(session, skip, limit)
    return passports


@router.get("/passports/{passport_id}", response_model=Passport)
async def get_passport_details(
        passport_id: int,
        session: SessionDep
):
    """Получить информацию о паспорте по ID"""
    passport = await get_passport(session, passport_id)
    if not passport:
        raise HTTPException(status_code=404, detail="Passport not found")
    return passport


@router.post("/passports/", response_model=Passport)
async def create_new_passport(
        passport: PassportBase,
        session: SessionDep
):
    """Создать новый паспорт"""
    db_passport = await create_passport(session, passport.dict())
    return db_passport


@router.put("/passports/{passport_id}", response_model=Passport)
async def update_passport_details(
        passport_id: int,
        passport: PassportBase,
        session: SessionDep
):
    """Обновить информацию о паспорте"""
    updated_passport = await update_passport(
        session, passport_id, passport.dict(exclude_unset=True)
    )
    if not updated_passport:
        raise HTTPException(status_code=404, detail="Passport not found")
    return updated_passport


@router.delete("/passports/{passport_id}")
async def delete_passport_by_id(
        passport_id: int,
        session: SessionDep
):
    """Удалить паспорт"""
    deleted_passport = await delete_passport(session, passport_id)
    if not deleted_passport:
        raise HTTPException(status_code=404, detail="Passport not found")
    return {"message": "Passport deleted successfully"}


@router.get("/rightsholders/", response_model=list[RightsHolder])
async def list_rights_holders(
        session: SessionDep,
        skip: int = 0,
        limit: int = 100
):
    """Получить список правообладателей"""
    rightsholders = await get_rights_holders(session, skip, limit)
    return rightsholders


@router.get("/rightsholders/{holder_id}", response_model=RightsHolder)
async def get_rights_holder_details(
        holder_id: int,
        session: SessionDep
):
    """Получить информацию о правообладателе по ID"""
    rightsholder = await get_rights_holder(session, holder_id)
    if not rightsholder:
        raise HTTPException(status_code=404, detail="Rights holder not found")
    return rightsholder


@router.post("/rightsholders/", response_model=RightsHolder)
async def create_new_rights_holder(
        rightsholder: RightsHolderBase,
        session: SessionDep
):
    """Создать нового правообладателя"""
    db_rightsholder = await create_rights_holder(session, rightsholder.dict())
    return db_rightsholder


@router.get("/statuses/", response_model=list[Status])
async def list_statuses(
        session: SessionDep
):
    """Получить список статусов"""
    statuses = await get_statuses(session)
    return statuses


@router.get("/statuses/{status_id}", response_model=Status)
async def get_status_details(
        status_id: int,
        session: SessionDep
):
    """Получить информацию о статусе по ID"""
    status = await get_status(session, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status


@router.post("/statuses/", response_model=Status)
async def create_new_status(
        status: StatusBase,
        session: SessionDep
):
    """Создать новый статус"""
    db_status = await create_status(session, status.dict())
    return db_status


@router.get("/types/", response_model=list[PatentType])
async def list_types(
        session: SessionDep
):
    """Получить список типов патентов"""
    types = await get_patent_types(session)
    return types


@router.get("/types/{type_id}", response_model=PatentType)
async def get_type_details(
        type_id: int,
        session: SessionDep
):
    """Получить информацию о типе патента по ID"""
    type_obj = await get_patent_type(session, type_id)
    if not type_obj:
        raise HTTPException(status_code=404, detail="Patent type not found")
    return type_obj


@router.post("/types/", response_model=PatentType)
async def create_new_type(
        type_obj: PatentTypeBase,
        session: SessionDep
):
    """Создать новый тип патента"""
    db_type = await create_patent_type(session, type_obj.model_dump())
    return db_type


@router.get("/positions/", response_model=list[Position])
async def list_positions(
        session: SessionDep
):
    """Получить список должностей"""
    positions = await get_positions(session)
    return positions