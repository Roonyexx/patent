from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.models import User
from src.core.security import hash_password


async def get_user_by_id(session: AsyncSession, user_id: int):
    """Get user by ID"""
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_username(session: AsyncSession, username: str):
    """Get user by username"""
    result = await session.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def get_user_by_email(session: AsyncSession, email: str):
    """Get user by email"""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(
    session: AsyncSession,
    email: str,
    username: str,
    password: str,
    user_type: str,
    employee_id: int = None,
    author_id: int = None
):
    """Create new user"""
    hashed_password = hash_password(password)
    db_user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        user_type=user_type,
        employee_id=employee_id,
        author_id=author_id,
        is_active=True
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def update_user(session: AsyncSession, user_id: int, update_data: dict):
    """Update user"""
    db_user = await get_user_by_id(session, user_id)
    if not db_user:
        return None
    
    for key, value in update_data.items():
        if value is not None:
            if key == "password":
                setattr(db_user, "hashed_password", hash_password(value))
            else:
                setattr(db_user, key, value)
    
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def deactivate_user(session: AsyncSession, user_id: int):
    """Deactivate user"""
    db_user = await get_user_by_id(session, user_id)
    if not db_user:
        return None
    
    db_user.is_active = False
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def activate_user(session: AsyncSession, user_id: int):
    """Activate user"""
    db_user = await get_user_by_id(session, user_id)
    if not db_user:
        return None
    
    db_user.is_active = True
    await session.commit()
    await session.refresh(db_user)
    return db_user
