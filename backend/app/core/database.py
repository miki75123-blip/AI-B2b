"""
數據庫配置和會話管理
支持 SQLite（本地開發）和 PostgreSQL（生產環境）
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings

# 根據 URL 類型創建引擎
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite 配置
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite 特定
        echo=settings.DEBUG,
    )
else:
    # PostgreSQL 配置
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG,
    )

# SQLite 啟用外鍵約束
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# 創建會話工廠
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# 基礎模型
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    獲取數據庫會話的依賴注入函數
    
    Yields:
        Session: 數據庫會話
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db() -> None:
    """初始化數據庫"""
    Base.metadata.create_all(bind=engine)
