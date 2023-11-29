from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

app = FastAPI()

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model
class RequestCounter(Base):
    __tablename__ = "request_counter"
    id = Column(Integer, primary_key=True, index=True)
    count = Column(Integer, default=0)

# Create database tables
Base.metadata.create_all(bind=engine)

# Pydantic model for the API response
class RequestStatus(BaseModel):
    can_make_request: bool

# Function to check if a request can be made to the third-party API
def check_request_status():
    db = SessionLocal()
    counter = db.query(RequestCounter).first()

    # Check if the counter exists in the database
    if not counter:
        counter = RequestCounter(count=0)
        db.add(counter)
        db.commit()

    # Check if the counter has reached the limit
    if counter.count >= 3:
        # Check if the last request was made more than a minute ago
        if datetime.now() - timedelta(minutes=1) > counter.updated_at:
            counter.count = 0
            db.commit()
            return True
        else:
            return False

    return True

# API endpoint
@app.get("/check_request_status", response_model=RequestStatus)
def get_request_status():
    can_make_request = check_request_status()
    return {"can_make_request": can_make_request}