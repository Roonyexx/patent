from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.models import Employee, Author, RightsHolder, Status, PatentType, Position, Passport


async def get_passport(session: AsyncSession, passport_id: int):
    result = await session.execute(select(Passport).where(Passport.id == passport_id))
    return result.scalars().first()


async def get_passports(session: AsyncSession, skip: int = 0, limit: int = 100):
    result = await session.execute(select(Passport).offset(skip).limit(limit))
    return result.scalars().all()


async def create_passport(session: AsyncSession, passport_data: dict):
    db_passport = Passport(
        series=passport_data.get("series"),
        number=passport_data.get("number"),
        birth_date=passport_data.get("birth_date"),
        birth_place=passport_data.get("birth_place"),
        department_code=passport_data.get("department_code"),
        issued_by=passport_data.get("issued_by")
    )
    session.add(db_passport)
    await session.commit()
    await session.refresh(db_passport)
    return db_passport


async def update_passport(session: AsyncSession, passport_id: int, update_data: dict):
    db_passport = await get_passport(session, passport_id)
    if not db_passport:
        return None
    for key, value in update_data.items():
        if value is not None:
            setattr(db_passport, key, value)
    await session.commit()
    await session.refresh(db_passport)
    return db_passport


async def delete_passport(session: AsyncSession, passport_id: int):
    db_passport = await get_passport(session, passport_id)
    if db_passport:
        await session.delete(db_passport)
        await session.commit()
    return db_passport


async def get_employee(session: AsyncSession, employee_id: int):
    result = await session.execute(
        select(Employee)
        .where(Employee.id == employee_id)
        .options(
            selectinload(Employee.position),
            selectinload(Employee.passport)
        )
    )
    return result.scalars().first()


async def get_employees(
        session: AsyncSession,
        full_name: Optional[str] = None,
        passport_series: Optional[int] = None,
        passport_number: Optional[int] = None,
        position_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
):
    query = select(Employee).options(
        selectinload(Employee.position),
        selectinload(Employee.passport)
    )

    if full_name:
        query = query.where(Employee.full_name.ilike(f"%{full_name}%"))
    if position_id:
        query = query.where(Employee.position_id == position_id)
    if passport_series or passport_number:
        query = query.join(Passport, Employee.passport_id == Passport.id)
        if passport_series:
            query = query.where(Passport.series == passport_series)
        if passport_number:
            query = query.where(Passport.number == passport_number)

    result = await session.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def create_employee(session: AsyncSession, employee_data: dict):
    db_employee = Employee(
        full_name=employee_data.get("full_name"),
        passport_id=employee_data.get("passport_id"),
        position_id=employee_data.get("position_id"),
        employment_date=employee_data.get("employment_date"),
        phone_number=employee_data.get("phone_number")
    )
    session.add(db_employee)
    await session.commit()
    await session.refresh(db_employee)
    return db_employee


async def update_employee(session: AsyncSession, employee_id: int, update_data: dict):
    db_employee = await get_employee(session, employee_id)
    if not db_employee:
        return None
    for key, value in update_data.items():
        if value is not None:
            setattr(db_employee, key, value)
    await session.commit()
    await session.refresh(db_employee)
    return db_employee


async def delete_employee(session: AsyncSession, employee_id: int):
    db_employee = await get_employee(session, employee_id)
    if db_employee:
        await session.delete(db_employee)
        await session.commit()
    return db_employee


async def get_author(session: AsyncSession, author_id: int):
    result = await session.execute(
        select(Author)
        .where(Author.id == author_id)
        .options(selectinload(Author.passport))
    )
    return result.scalars().first()


async def get_authors(
        session: AsyncSession,
        full_name: Optional[str] = None,
        passport_series: Optional[int] = None,
        passport_number: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
):
    query = select(Author).options(
        selectinload(Author.passport)
    )

    if full_name:
        query = query.where(Author.full_name.ilike(f"%{full_name}%"))
    if passport_series or passport_number:
        query = query.join(Passport, Author.passport_id == Passport.id)
        if passport_series:
            query = query.where(Passport.series == passport_series)
        if passport_number:
            query = query.where(Passport.number == passport_number)

    result = await session.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def create_author(session: AsyncSession, author_data: dict):
    db_author = Author(
        full_name=author_data.get("full_name"),
        passport_id=author_data.get("passport_id")
    )
    session.add(db_author)
    await session.commit()
    await session.refresh(db_author)
    return db_author


async def update_author(session: AsyncSession, author_id: int, update_data: dict):
    db_author = await get_author(session, author_id)
    if not db_author:
        return None
    for key, value in update_data.items():
        if value is not None:
            setattr(db_author, key, value)
    await session.commit()
    await session.refresh(db_author)
    return db_author


async def delete_author(session: AsyncSession, author_id: int):
    db_author = await get_author(session, author_id)
    if db_author:
        await session.delete(db_author)
        await session.commit()
    return db_author


async def get_rights_holder(session: AsyncSession, holder_id: int):
    result = await session.execute(select(RightsHolder).where(RightsHolder.id == holder_id))
    return result.scalars().first()


async def get_rights_holders(session: AsyncSession, skip: int = 0, limit: int = 100):
    result = await session.execute(select(RightsHolder).offset(skip).limit(limit))
    return result.scalars().all()


async def create_rights_holder(session: AsyncSession, holder_data: dict):
    db_holder = RightsHolder(name=holder_data.get("name"))
    session.add(db_holder)
    await session.commit()
    await session.refresh(db_holder)
    return db_holder


async def update_rights_holder(session: AsyncSession, holder_id: int, update_data: dict):
    db_holder = await get_rights_holder(session, holder_id)
    if not db_holder:
        return None
    for key, value in update_data.items():
        if value is not None:
            setattr(db_holder, key, value)
    await session.commit()
    await session.refresh(db_holder)
    return db_holder


async def delete_rights_holder(session: AsyncSession, holder_id: int):
    db_holder = await get_rights_holder(session, holder_id)
    if db_holder:
        await session.delete(db_holder)
        await session.commit()
    return db_holder


async def get_status(session: AsyncSession, status_id: int):
    result = await session.execute(select(Status).where(Status.id == status_id))
    return result.scalars().first()


async def get_statuses(session: AsyncSession, skip: int = 0, limit: int = 100):
    result = await session.execute(select(Status).offset(skip).limit(limit))
    return result.scalars().all()


async def create_status(session: AsyncSession, status_data: dict):
    db_status = Status(name=status_data.get("name"))
    session.add(db_status)
    await session.commit()
    await session.refresh(db_status)
    return db_status


async def update_status(session: AsyncSession, status_id: int, update_data: dict):
    db_status = await get_status(session, status_id)
    if not db_status:
        return None
    for key, value in update_data.items():
        if value is not None:
            setattr(db_status, key, value)
    await session.commit()
    await session.refresh(db_status)
    return db_status


async def delete_status(session: AsyncSession, status_id: int):
    db_status = await get_status(session, status_id)
    if db_status:
        await session.delete(db_status)
        await session.commit()
    return db_status


async def get_patent_type(session: AsyncSession, type_id: int):
    result = await session.execute(select(PatentType).where(PatentType.id == type_id))
    return result.scalars().first()


async def get_patent_types(session: AsyncSession, skip: int = 0, limit: int = 100):
    result = await session.execute(select(PatentType).offset(skip).limit(limit))
    return result.scalars().all()


async def create_patent_type(session: AsyncSession, type_data: dict):
    db_type = PatentType(name=type_data.get("name"))
    session.add(db_type)
    await session.commit()
    await session.refresh(db_type)
    return db_type


async def update_patent_type(session: AsyncSession, type_id: int, update_data: dict):
    db_type = await get_patent_type(session, type_id)
    if not db_type:
        return None
    for key, value in update_data.items():
        if value is not None:
            setattr(db_type, key, value)
    await session.commit()
    await session.refresh(db_type)
    return db_type


async def delete_patent_type(session: AsyncSession, type_id: int):
    db_type = await get_patent_type(session, type_id)
    if db_type:
        await session.delete(db_type)
        await session.commit()
    return db_type


async def get_position(session: AsyncSession, position_id: int):
    result = await session.execute(select(Position).where(Position.id == position_id))
    return result.scalars().first()


async def get_positions(session: AsyncSession, skip: int = 0, limit: int = 100):
    result = await session.execute(select(Position).offset(skip).limit(limit))
    return result.scalars().all()


async def create_position(session: AsyncSession, position_data: dict):
    db_position = Position(name=position_data.get("name"))
    session.add(db_position)
    await session.commit()
    await session.refresh(db_position)
    return db_position