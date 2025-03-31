from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Engineer(Base):
    __tablename__ = 'engineers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    company_name = Column(String)
    date_of_birth = Column(Date)
    address = Column(String)
    position_and_rank = Column(String)
    responsible_technical_manager = Column(String)
    experience = Column(String)
    field_name = Column(String)
    evaluation_target = Column(String)
    pdf_file = Column(String)
    selected = Column(Boolean)
    technical_grades = relationship("TechnicalGrade", back_populates="engineer", cascade="all, delete-orphan")
    technical_qualifications = relationship("TechnicalQualification", back_populates="engineer", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="engineer", cascade="all, delete-orphan")
    technical_sector_participation = relationship("TechnicalSectorParticipation", back_populates="engineer", cascade="all, delete-orphan")
    job_sector_participation = relationship("JobSectorParticipation", back_populates="engineer", cascade="all, delete-orphan")
    specialized_field_participation = relationship("SpecializedFieldParticipation", back_populates="engineer", cascade="all, delete-orphan")
    construction_type_participation = relationship("ConstructionTypeParticipation", back_populates="engineer", cascade="all, delete-orphan")
    education_and_training = relationship("EducationAndTraining", back_populates="engineer", cascade="all, delete-orphan")
    awards = relationship("Award", back_populates="engineer", cascade="all, delete-orphan")
    sanctions = relationship("Sanction", back_populates="engineer", cascade="all, delete-orphan")
    workplace = relationship("Workplace", back_populates="engineer", cascade="all, delete-orphan")
    project_details = relationship("ProjectDetail", back_populates="engineer", cascade="all, delete-orphan")

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
