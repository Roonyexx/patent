from src.db.database import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = "User"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_type = Column(String, nullable=False)  # 'employee' или 'author'
    employee_id = Column(Integer, ForeignKey("Employee.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=True)
    author_id = Column(Integer, ForeignKey("Author.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=True)
    
    employee = relationship("Employee", foreign_keys=[employee_id])
    author = relationship("Author", foreign_keys=[author_id])


class Position(Base):
    __tablename__ = "Position"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    
    employees = relationship("Employee", back_populates="position")


class Passport(Base):
    __tablename__ = "Passport"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    series = Column(Integer)
    number = Column(Integer)
    birth_date = Column(Date)
    birth_place = Column(String)
    department_code = Column(Integer)
    issued_by = Column(String)
    
    authors = relationship("Author", back_populates="passport")
    employees = relationship("Employee", back_populates="passport")


class Author(Base):
    __tablename__ = "Author"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    passport_id = Column(Integer, ForeignKey("Passport.id", ondelete="CASCADE", onupdate="RESTRICT"))
    
    passport = relationship("Passport", back_populates="authors")
    patent_authors = relationship("PatentAuthor", back_populates="author")


class Status(Base):
    __tablename__ = "Status"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    
    applications = relationship("Application", back_populates="status")
    patents = relationship("Patent", back_populates="status")


class Employee(Base):
    __tablename__ = "Employee"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    employment_date = Column(Date)
    termination_date = Column(Date)
    phone_number = Column(String)
    position_id = Column(Integer, ForeignKey("Position.id", ondelete="RESTRICT", onupdate="RESTRICT"))
    passport_id = Column(Integer, ForeignKey("Passport.id", ondelete="CASCADE", onupdate="RESTRICT"))
    
    position = relationship("Position", back_populates="employees")
    passport = relationship("Passport", back_populates="employees")
    applications = relationship("Application", back_populates="employee")


class Application(Base):
    __tablename__ = "Application"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    documents = Column(Text)
    modification_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expert_conclusion = Column(Text)
    status_id = Column(Integer, ForeignKey("Status.id", ondelete="RESTRICT", onupdate="RESTRICT"))
    employee_id = Column(Integer, ForeignKey("Employee.id", ondelete="RESTRICT", onupdate="RESTRICT"))
    author_id = Column(Integer, ForeignKey("Author.id", ondelete="RESTRICT", onupdate="RESTRICT"))
    
    status = relationship("Status", back_populates="applications")
    employee = relationship("Employee", back_populates="applications")
    author = relationship("Author")
    patent = relationship("Patent", uselist=False, back_populates="application")


class RightsHolder(Base):
    __tablename__ = "RightsHolder"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    
    patents = relationship("Patent", back_populates="rights_holder")


class PatentType(Base):
    __tablename__ = "PatentType"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    
    patents = relationship("Patent", back_populates="patent_type")


class Patent(Base):
    __tablename__ = "Patent"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    issue_date = Column(Date)
    expiration_date = Column(Date)
    description = Column(String)
    rights_holder_id = Column(Integer, ForeignKey("RightsHolder.id", ondelete="RESTRICT", onupdate="RESTRICT"))
    patent_type_id = Column(Integer, ForeignKey("PatentType.id", ondelete="RESTRICT", onupdate="RESTRICT"))
    status_id = Column(Integer, ForeignKey("Status.id", ondelete="RESTRICT", onupdate="RESTRICT"))
    application_id = Column(Integer, ForeignKey("Application.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    
    rights_holder = relationship("RightsHolder", back_populates="patents")
    patent_type = relationship("PatentType", back_populates="patents")
    status = relationship("Status", back_populates="patents")
    application = relationship("Application", back_populates="patent")
    patent_authors = relationship("PatentAuthor", back_populates="patent")


class PatentAuthor(Base):
    __tablename__ = "PatentAuthor"
    
    author_id = Column(Integer, ForeignKey("Author.id", ondelete="CASCADE", onupdate="RESTRICT"), primary_key=True)
    patent_id = Column(Integer, ForeignKey("Patent.id", ondelete="RESTRICT", onupdate="RESTRICT"), primary_key=True)
    is_rights_holder = Column(Boolean, default=False)
    participation_percentage = Column(Numeric(5, 2))
    
    author = relationship("Author", back_populates="patent_authors")
    patent = relationship("Patent", back_populates="patent_authors")
