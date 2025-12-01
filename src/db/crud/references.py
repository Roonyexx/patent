from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.models import Employee, Author, RightsHolder, Status, PatentType, Position


async def get_employee(session: AsyncSession, employee_id: int):
    """Get employee by ID"""
    result = await session.execute(select(Employee).where(Employee.id == employee_id))
    return result.scalars().first()


async def get_employees(session: AsyncSession, skip: int = 0, limit: int = 100):
    """Get list of employees"""
    result = await session.execute(select(Employee).offset(skip).limit(limit))
    return result.scalars().all()


async def create_employee(session: AsyncSession, employee_data: dict):
    """Create new employee"""
    db_employee = Employee(
        full_name=employee_data.get("full_name"),
        employment_date=employee_data.get("employment_date"),
        termination_date=employee_data.get("termination_date"),
        phone_number=employee_data.get("phone_number"),
        position_id=employee_data.get("position_id"),
        passport_id=employee_data.get("passport_id")
    )
    session.add(db_employee)
    await session.commit()
    await session.refresh(db_employee)
    return db_employee


async def update_employee(session: AsyncSession, employee_id: int, update_data: dict):
    """Update employee"""
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
    """Delete employee"""
    db_employee = await get_employee(session, employee_id)
    if db_employee:
        await session.delete(db_employee)
        await session.commit()
    return db_employee


async def get_author(session: AsyncSession, author_id: int):
    """Get author by ID"""
    result = await session.execute(select(Author).where(Author.id == author_id))
    return result.scalars().first()


async def get_authors(session: AsyncSession, skip: int = 0, limit: int = 100):
    """Get list of authors"""
    result = await session.execute(select(Author).offset(skip).limit(limit))
    return result.scalars().all()


async def create_author(session: AsyncSession, author_data: dict):
    """Create new author"""
    db_author = Author(
        full_name=author_data.get("full_name"),
        passport_id=author_data.get("passport_id")
    )
    session.add(db_author)
    await session.commit()
    await session.refresh(db_author)
    return db_author


async def update_author(session: AsyncSession, author_id: int, update_data: dict):
    """Update author"""
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
    """Delete author"""
    db_author = await get_author(session, author_id)
    if db_author:
        await session.delete(db_author)
        await session.commit()
    return db_author


async def get_rights_holder(session: AsyncSession, holder_id: int):
    """Get rights holder by ID"""
    result = await session.execute(select(RightsHolder).where(RightsHolder.id == holder_id))
    return result.scalars().first()


async def get_rights_holders(session: AsyncSession, skip: int = 0, limit: int = 100):
    """Get list of rights holders"""
    result = await session.execute(select(RightsHolder).offset(skip).limit(limit))
    return result.scalars().all()


async def create_rights_holder(session: AsyncSession, holder_data: dict):
    """Create new rights holder"""
    db_holder = RightsHolder(
        name=holder_data.get("name")
    )
    session.add(db_holder)
    await session.commit()
    await session.refresh(db_holder)
    return db_holder


async def update_rights_holder(session: AsyncSession, holder_id: int, update_data: dict):
    """Update rights holder"""
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
    """Delete rights holder"""
    db_holder = await get_rights_holder(session, holder_id)
    if db_holder:
        await session.delete(db_holder)
        await session.commit()
    return db_holder


async def get_status(session: AsyncSession, status_id: int):
    """Get status by ID"""
    result = await session.execute(select(Status).where(Status.id == status_id))
    return result.scalars().first()


async def get_statuses(session: AsyncSession, skip: int = 0, limit: int = 100):
    """Get list of statuses"""
    result = await session.execute(select(Status).offset(skip).limit(limit))
    return result.scalars().all()


async def create_status(session: AsyncSession, status_data: dict):
    """Create new status"""
    db_status = Status(
        name=status_data.get("name")
    )
    session.add(db_status)
    await session.commit()
    await session.refresh(db_status)
    return db_status


async def update_status(session: AsyncSession, status_id: int, update_data: dict):
    """Update status"""
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
    """Delete status"""
    db_status = await get_status(session, status_id)
    if db_status:
        await session.delete(db_status)
        await session.commit()
    return db_status


async def get_patent_type(session: AsyncSession, type_id: int):
    """Get patent type by ID"""
    result = await session.execute(select(PatentType).where(PatentType.id == type_id))
    return result.scalars().first()


async def get_patent_types(session: AsyncSession, skip: int = 0, limit: int = 100):
    """Get list of patent types"""
    result = await session.execute(select(PatentType).offset(skip).limit(limit))
    return result.scalars().all()


async def create_patent_type(session: AsyncSession, type_data: dict):
    """Create new patent type"""
    db_type = PatentType(
        name=type_data.get("name")
    )
    session.add(db_type)
    await session.commit()
    await session.refresh(db_type)
    return db_type


async def update_patent_type(session: AsyncSession, type_id: int, update_data: dict):
    """Update patent type"""
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
    """Delete patent type"""
    db_type = await get_patent_type(session, type_id)
    if db_type:
        await session.delete(db_type)
        await session.commit()
    return db_type


async def get_position(session: AsyncSession, position_id: int):
    """Get position by ID"""
    result = await session.execute(select(Position).where(Position.id == position_id))
    return result.scalars().first()


async def get_positions(session: AsyncSession, skip: int = 0, limit: int = 100):
    """Get list of positions"""
    result = await session.execute(select(Position).offset(skip).limit(limit))
    return result.scalars().all()


async def create_position(session: AsyncSession, position_data: dict):
    """Create new position"""
    db_position = Position(
        name=position_data.get("name")
    )
    session.add(db_position)
    await session.commit()
    await session.refresh(db_position)
    return db_position


async def create_employee_internal(
    session: AsyncSession,
    full_name: str,
    position_id: int,
    employment_date=None,
    phone_number=None
):
    """
    Create employee record during registration
    Used internally by auth.register endpoint
    """
    db_employee = Employee(
        full_name=full_name,
        employment_date=employment_date,
        phone_number=phone_number,
        position_id=position_id
    )
    session.add(db_employee)
    await session.commit()
    await session.refresh(db_employee)
    return db_employee


async def create_author_internal(
    session: AsyncSession,
    full_name: str
):
    """
    Create author record during registration
    Used internally by auth.register endpoint
    """
    db_author = Author(
        full_name=full_name
    )
    session.add(db_author)
    await session.commit()
    await session.refresh(db_author)
    return db_author
