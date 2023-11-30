from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import SingletonThreadPool
from datetime import datetime, timedelta

app = FastAPI()

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=SingletonThreadPool)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = SessionLocal.query_property()

# Database model
class RequestCounter(Base):
    __tablename__ = "request_counter"
    id = Column(Integer, primary_key=True, index=True)
    count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.now) 

# Create database tables
Base.metadata.create_all(bind=engine)


# Pydantic model for the API response
class Response(BaseModel):
    can_make_request: bool

# Function to check if a request can be made to the third-party API
def check_request_limit():
    db = SessionLocal()
    counter = db.query(RequestCounter).first()

    # Check if the request count exceeds the limit
    if counter.count >= 5:
        # Check if the ban period has expired
        if datetime.now() - timedelta(minutes=20) > counter.updated_at:
            # Reset the counter if the ban period has expired
            counter.count = 0
            db.commit()
            return True
        else:
            return False

    return True

# API endpoint
@app.get("/check_request_limit")
def check_request_limit_endpoint():
    can_make_request = check_request_limit()
    return Response(can_make_request=can_make_request)
