"""
FastAPI 主應用程序
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.core.config import settings
from app.core.database import engine, Base
from app.api import api_router


# 配置日誌
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.DEBUG else "INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程序生命周期"""
    # 啟動時
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # 創建數據庫表
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    yield
    
    # 關閉時
    logger.info("Shutting down...")


# 創建 FastAPI 應用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    AI LeadGen Agent - 全自動 B2B 潛在客戶開發系統
    
    ## 功能
    
    - 🤖 **Scout Agent**: 自動從 B2B 平台爬取供應商資訊
    - ✍️ **Writer Agent**: AI 生成個性化銷售郵件
    - 📧 **Sender Agent**: 智能郵件發送與追蹤
    - 📊 **Optimizer Agent**: 持續優化策略提升效果
    
    ## API
    
    所有 API 都需要認證。請在請求頭中添加:
    `Authorization: Bearer <your_token>`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加中間件
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 包含 API 路由
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """根路徑"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


# 錯誤處理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局異常處理"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "detail": "Internal server error",
        "message": str(exc) if settings.DEBUG else "An error occurred"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
