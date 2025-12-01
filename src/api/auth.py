from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from src.api.depends import SessionDep, CurrentUserDep
from src.schemas.patent import (
    UserRegister, UserLogin, TokenResponse, TokenRefresh, UserResponse
)
from src.db.crud.user import (
    get_user_by_username, get_user_by_email, create_user, get_user_by_id
)
from src.db.crud.references import (
    get_employee, get_author, get_position, 
    create_employee_internal, create_author_internal
)
from src.core.security import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    verify_token
)

router = APIRouter()


@router.get("/health")
async def health_check():
    """API health check"""
    return {"status": "ok", "message": "Patent API is running"}


@router.post("/register", response_model=TokenResponse)
async def register(
    registration: UserRegister,
    session: SessionDep
):
    """Register new user (employee or author)"""
    existing_user = await get_user_by_username(session, registration.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    existing_email = await get_user_by_email(session, registration.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if registration.user_type not in ["employee", "author"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_type must be 'employee' or 'author'"
        )
    

    if not registration.full_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="full_name is required"
        )
    
    employee_id = None
    author_id = None
    position_name = None
    
    if registration.user_type == "employee":
        if not registration.position_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="position_id is required for employees"
            )
        

        position = await get_position(session, registration.position_id)
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Position not found"
            )
        position_name = position.name

        employee = await create_employee_internal(
            session,
            full_name=registration.full_name,
            employment_date=registration.employment_date,
            phone_number=registration.phone_number,
            position_id=registration.position_id
        )
        employee_id = employee.id
        
    else:  
        author = await create_author_internal(
            session,
            full_name=registration.full_name
        )
        author_id = author.id
    
    new_user = await create_user(
        session=session,
        email=registration.email,
        username=registration.username,
        password=registration.password,
        user_type=registration.user_type,
        employee_id=employee_id,
        author_id=author_id
    )

    access_token = create_access_token(
        user_id=new_user.id,
        username=new_user.username,
        user_type=new_user.user_type,
        position_name=position_name,
        employee_id=employee_id,
        author_id=author_id
    )
    
    refresh_token = create_refresh_token(new_user.id, new_user.username)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=new_user.id,
        username=new_user.username,
        user_type=new_user.user_type
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    session: SessionDep
):
    """Login with username and password"""
    user = await get_user_by_username(session, credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    position_name = None
    if user.user_type == "employee" and user.employee:
        if user.employee.position:
            position_name = user.employee.position.name
    
    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        user_type=user.user_type,
        position_name=position_name,
        employee_id=user.employee_id,
        author_id=user.author_id
    )
    
    refresh_token = create_refresh_token(user.id, user.username)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        user_type=user.user_type
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_request: TokenRefresh,
    session: SessionDep
):
    """
    Refresh access token using refresh token
    """
    token_data = verify_token(refresh_request.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    user = await get_user_by_id(session, token_data.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    position_name = None
    if user.user_type == "employee" and user.employee:
        if user.employee.position:
            position_name = user.employee.position.name
    
    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        email=user.email,
        user_type=user.user_type,
        position_name=position_name,
        employee_id=user.employee_id,
        author_id=user.author_id
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_request.refresh_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        user_type=user.user_type
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUserDep,
    session: SessionDep
):
    """Get current user information from JWT token"""
    user = await get_user_by_id(session, current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        user_type=user.user_type,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.post("/logout")
async def logout(current_user: CurrentUserDep):
    return {"message": f"User {current_user.username} logged out successfully"}






