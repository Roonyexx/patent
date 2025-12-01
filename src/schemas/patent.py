from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime



class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    user_type: str  
    

    full_name: Optional[str] = None
    employment_date: Optional[date] = None
    phone_number: Optional[str] = None
    position_id: Optional[int] = None



class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    user_type: str


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    user_type: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True



class PositionBase(BaseModel):
    name: str

class Position(PositionBase):
    id: int
    
    class Config:
        from_attributes = True



class PassportBase(BaseModel):
    series: Optional[int] = None
    number: Optional[int] = None
    birth_date: Optional[date] = None
    birth_place: Optional[str] = None
    department_code: Optional[int] = None
    issued_by: Optional[str] = None

class Passport(PassportBase):
    id: int
    
    class Config:
        from_attributes = True



class AuthorBase(BaseModel):
    full_name: str
    passport_id: Optional[int] = None

class Author(AuthorBase):
    id: int
    
    class Config:
        from_attributes = True



class StatusBase(BaseModel):
    name: str

class Status(StatusBase):
    id: int
    
    class Config:
        from_attributes = True



class EmployeeBase(BaseModel):
    full_name: str
    employment_date: Optional[date] = None
    termination_date: Optional[date] = None
    phone_number: Optional[int] = None
    position_id: Optional[int] = None
    passport_id: Optional[int] = None

class Employee(EmployeeBase):
    id: int
    
    class Config:
        from_attributes = True



class ApplicationBase(BaseModel):
    documents: Optional[str] = None
    expert_conclusion: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class PatentBrief(BaseModel):
    id: int
    title: Optional[str] = None
    
    class Config:
        from_attributes = True

class Application(ApplicationBase):
    id: int
    submission_date: datetime
    modification_date: Optional[datetime] = None
    status_id: Optional[int] = None
    status: Optional[Status] = None
    employee_id: Optional[int] = None
    author_id: Optional[int] = None
    patent: Optional[PatentBrief] = None
    
    class Config:
        from_attributes = True



class RightsHolderBase(BaseModel):
    name: str

class RightsHolder(RightsHolderBase):
    id: int
    
    class Config:
        from_attributes = True



class PatentTypeBase(BaseModel):
    name: Optional[str] = None

class PatentType(PatentTypeBase):
    id: int
    
    class Config:
        from_attributes = True


class PatentBase(BaseModel):
    title: Optional[str] = None
    issue_date: Optional[date] = None
    description: Optional[str] = None
    rights_holder_id: Optional[int] = None
    patent_type_id: Optional[int] = None
    application_id: int

class PatentCreate(PatentBase):
    pass

class Patent(PatentBase):
    id: int
    expiration_date: Optional[date] = None
    status_id: Optional[int] = None
    status: Optional[Status] = None
    
    class Config:
        from_attributes = True



class PatentAuthorBase(BaseModel):
    is_rights_holder: bool = False
    participation_percentage: Optional[float] = None
    author_id: int
    patent_id: int

class PatentAuthor(PatentAuthorBase):
    
    class Config:
        from_attributes = True
