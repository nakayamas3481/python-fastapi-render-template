from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from ai import get_vector_store, inmemory_vector_store
from db import get_db_session
from main import app
from config import settings
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(str(settings.DATABASE_URL))
    yield engine

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    transaction = connection.begin()
    
    try:
        yield session
    finally:
        if transaction.is_active:
                transaction.rollback()
        session.close()
        connection.close()

@pytest.fixture(scope="function")
def vector_store():
    yield from inmemory_vector_store()

@pytest.fixture(scope="function")
def client(db_session, vector_store):
    def override_get_db():
        yield db_session

    def override_vector_store():
        yield vector_store
    
    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_vector_store] = override_vector_store
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()