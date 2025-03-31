from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, Float
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
    technical_qualifications = relationship("Qualification", back_populates="engineer", cascade="all, delete-orphan")
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

class TechnicalGrade(Base):
    __tablename__ = 'technical_grades'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    grade_type = Column(String)  # Job Field|Technical Sector, Specialized Field, etc.
    field = Column(String)       # Construction, Industry, Road and Airport, etc.
    grade = Column(String)       # Professional Engineer, etc.
    engineer = relationship("Engineer", back_populates="technical_grades")

class Qualification(Base):
    __tablename__ = 'qualifications'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    title = Column(String)  # Type and Grade
    acquisition_date = Column(Date)  # Pass Date
    registration_number = Column(String)
    engineer = relationship("Engineer", back_populates="technical_qualifications")

class Education(Base):
    __tablename__ = 'education'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    graduation_date = Column(Date)
    school_name = Column(String)
    major = Column(String)  # Department (Major)
    degree = Column(String)
    engineer = relationship("Engineer", back_populates="education")

class TechnicalSectorParticipation(Base):
    __tablename__ = 'technical_sector_participation'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    technical_sector = Column(String)
    participation_days = Column(String)
    engineer = relationship("Engineer", back_populates="technical_sector_participation")

class JobSectorParticipation(Base):
    __tablename__ = 'job_sector_participation'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    job = Column(String)
    participation_days = Column(String)
    engineer = relationship("Engineer", back_populates="job_sector_participation")

class SpecializedFieldParticipation(Base):
    __tablename__ = 'specialized_field_participation'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    specialized_field = Column(String)
    participation_days = Column(String)
    engineer = relationship("Engineer", back_populates="specialized_field_participation")

class ConstructionTypeParticipation(Base):
    __tablename__ = 'construction_type_participation'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    construction_type = Column(String)
    participation_days = Column(String)
    engineer = relationship("Engineer", back_populates="construction_type_participation")

class EducationAndTraining(Base):
    __tablename__ = 'education_and_training'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    training_period = Column(String)
    course_name = Column(String)
    institution_name = Column(String)
    completion_number = Column(String)
    training_field = Column(String)
    engineer = relationship("Engineer", back_populates="education_and_training")

class Award(Base):
    __tablename__ = 'awards'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    date = Column(Date)
    type_and_basis = Column(String)
    awarding_institution = Column(String)
    engineer = relationship("Engineer", back_populates="awards")

class Sanction(Base):
    __tablename__ = 'sanctions'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    penalty_points = Column(String)
    date = Column(Date)
    type = Column(String)
    sanction_period = Column(String)
    basis = Column(String)
    sanctioning_institution = Column(String)
    engineer = relationship("Engineer", back_populates="sanctions")

class Workplace(Base):
    __tablename__ = 'workplace'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    workplace_experience_period = Column(String)
    workplace_company_name = Column(String)
    engineer = relationship("Engineer", back_populates="workplace")

class ProjectDetail(Base):
    __tablename__ = 'project_details'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    service_name = Column(String)
    project_type = Column(String)
    company_name = Column(String)
    representative_contractor = Column(String)
    contract_number = Column(String)
    service_number = Column(String)
    equity_ratio = Column(Float)
    service_overview = Column(String)
    total_investigation_length = Column(Float)
    construction_type = Column(String)
    client = Column(String)
    issuing_department = Column(String)
    contract_date = Column(Date)
    contract_period = Column(String)
    contract_amount = Column(String)
    performance = Column(String)
    participation_period = Column(String)
    participation_days = Column(Integer)
    engineering_business_category = Column(String)
    engineering_activity_type = Column(String)
    technical_sector = Column(String)
    specialized_field = Column(String)
    position = Column(String)
    engineer = relationship("Engineer", back_populates="project_details")
