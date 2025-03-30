import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base

DB_FILE = "engineers.db"

def init_database():
    # Create database engine
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), DB_FILE)
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Create tables only if they don't exist
    if not os.path.exists(db_path):
        Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    return Session()
