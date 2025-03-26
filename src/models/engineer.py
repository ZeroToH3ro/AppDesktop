from sqlalchemy import Column, Integer, String, JSON, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Engineer(Base):
    __tablename__ = 'engineers'
    
    id = Column(Integer, primary_key=True)
    person_name = Column(String)
    birth_date = Column(Date)
    address = Column(String)
    associated_company = Column(String)
    technical_grades = Column(JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'person_name': self.person_name,
            'birth_date': str(self.birth_date) if self.birth_date else None,
            'address': self.address,
            'associated_company': self.associated_company,
            'technical_grade': self.technical_grades.get('grade', [''])[0] if self.technical_grades else ''
        }
