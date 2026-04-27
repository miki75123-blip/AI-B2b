"""
用戶模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    """用戶模型"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    company_name = Column(String(255))
    company_website = Column(String(500))
    company_description = Column(Text)
    
    # 狀態
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # 郵件配置
    sendgrid_api_key = Column(String(500), nullable=True)
    email_from_address = Column(String(255), nullable=True)
    email_from_name = Column(String(200), nullable=True)
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # 關係
    campaigns = relationship("Campaign", back_populates="owner", cascade="all, delete-orphan")
    suppliers = relationship("Supplier", back_populates="owner", cascade="all, delete-orphan")
    email_templates = relationship("EmailTemplate", back_populates="owner", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"
