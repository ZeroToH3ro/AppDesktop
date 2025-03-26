from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.engineer import Base

def init_db():
    engine = create_engine('sqlite:///engineers.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
