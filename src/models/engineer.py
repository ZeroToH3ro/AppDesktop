from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from .base import Base

class Engineer(Base):
    __tablename__ = 'engineers'
    id = Column(Integer, primary_key=True)
    person_name = Column(String)
    birth_date = Column(Date)
    address = Column(String)
    associated_company = Column(String)
    currency_unit = Column(String, default='백만원')
    technical_grades = Column(String)
    position_title = Column(String)
    expertise_area = Column(String)
    project_lead = Column(String)
    experience_summary = Column(String)
    participation_days = Column(String)
    participation_details = Column(String)
    qualifications = relationship("Qualification", back_populates="engineer", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="engineer", cascade="all, delete-orphan")
    employment = relationship("Employment", back_populates="engineer", cascade="all, delete-orphan")
    training = relationship("Training", back_populates="engineer", cascade="all, delete-orphan")

class Qualification(Base):
    __tablename__ = 'qualifications'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    title = Column(String)
    acquisition_date = Column(Date)
    registration_number = Column(String)
    engineer = relationship("Engineer", back_populates="qualifications")

class Education(Base):
    __tablename__ = 'education'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    graduation_date = Column(Date)
    institution = Column(String)
    major = Column(String)
    degree = Column(String)
    engineer = relationship("Engineer", back_populates="education")

class Employment(Base):
    __tablename__ = 'employment'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    period = Column(String)  # Keep as string since it's a period range
    company = Column(String)
    engineer = relationship("Engineer", back_populates="employment")

class Training(Base):
    __tablename__ = 'training'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    course = Column(String)
    period = Column(String)  # Keep as string since it's a period range
    organization = Column(String)
    engineer = relationship("Engineer", back_populates="training")
