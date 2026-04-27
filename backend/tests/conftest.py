"""
測試配置
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

# 測試數據庫 URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """創建測試數據庫會話"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """創建測試客戶端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """創建測試用戶並返回認證頭"""
    # 註冊用戶
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    })
    
    # 登入
    response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "testpass123"
    })
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
