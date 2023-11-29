from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, Base, RequestCounter, SessionLocal 


# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create database tables for testing
Base.metadata.create_all(bind=engine)

# Override the original SessionLocal with the TestingSessionLocal
app.dependency_overrides[SessionLocal] = TestingSessionLocal

# Test the API endpoint
def test_check_request_limit():
    client = TestClient(app)

    # Test when the request count is below the limit
    response = client.get("/check_request_limit")
    assert response.status_code == 200
    assert response.json() == {"can_make_request": True}

    # Test when the request count reaches the limit
    db = TestingSessionLocal()
    counter = db.query(RequestCounter).first()
    counter.count = 5
    db.commit()

    response = client.get("/check_request_limit")
    assert response.status_code == 200
    assert response.json() == {"can_make_request": False}

    # Test when the ban period has expired
    counter.updated_at = datetime.now() - timedelta(minutes=21)
    db.commit()

    response = client.get("/check_request_limit")
    assert response.status_code == 200
    assert response.json() == {"can_make_request": True}

    # Test when the ban period has not expired
    counter.updated_at = datetime.now() - timedelta(minutes=19)
    db.commit()

    response = client.get("/check_request_limit")
    assert response.status_code == 200
    assert response.json() == {"can_make_request": False}