from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.db.database import getSession
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import verify_token, extract_token_from_header, TokenData
from src.db.crud.user import get_user_by_id

SessionDep = Annotated[AsyncSession, Depends(getSession)]
oauth2 = HTTPBearer()
TokenDep = Annotated[HTTPAuthorizationCredentials, Depends(oauth2)]


async def get_current_user(
    session: SessionDep,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2)
) -> TokenData:
    """Get current user from JWT token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    token_data = verify_token(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user_by_id(session, token_data.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not active",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


async def get_employee_user(
    current_user: Annotated[TokenData, Depends(get_current_user)]
) -> TokenData:
    """Require user to be employee"""
    if current_user.user_type != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employees can access this endpoint"
        )
    return current_user


async def get_author_user(
    current_user: Annotated[TokenData, Depends(get_current_user)]
) -> TokenData:
    """Require user to be author"""
    if current_user.user_type != "author":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authors can access this endpoint"
        )
    return current_user


CurrentUserDep = Annotated[TokenData, Depends(get_current_user)]
EmployeeUserDep = Annotated[TokenData, Depends(get_employee_user)]
AuthorUserDep = Annotated[TokenData, Depends(get_author_user)]
