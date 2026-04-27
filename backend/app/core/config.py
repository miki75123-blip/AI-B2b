"""
應用程序配置
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """應用程序配置"""
    
    # 應用信息
    APP_NAME: str = "AI LeadGen Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    SECRET_KEY: str = Field(default="change-me-in-production")
    
    # 數據庫
    DATABASE_URL: str = Field(
        default="sqlite:///./leadgen.db"
    )
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4")
    
    # SendGrid
    SENDGRID_API_KEY: str = Field(default="")
    SENDGRID_FROM_EMAIL: str = Field(default="noreply@example.com")
    
    # 爬蟲配置
    SCRAPER_USER_AGENT: str = Field(
        default="Mozilla/5.0 (compatible; AILeadGenBot/1.0)"
    )
    SCRAPER_DELAY_SECONDS: float = Field(default=2.0)
    
    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:5173")
    
    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小時
    
    # 開發模式標誌
    USE_FAKE_SCRAPER: bool = Field(default=True)
    USE_FAKE_EMAIL: bool = Field(default=True)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 允許額外字段
    
    @property
    def cors_origins_list(self) -> List[str]:
        """將 CORS_ORIGINS 字串轉換為列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """獲取緩存的設置實例"""
    return Settings()


# 全局設置實例
settings = get_settings()
