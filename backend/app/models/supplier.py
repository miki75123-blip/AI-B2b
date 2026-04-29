"""
供應商模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class SourcePlatform(enum.Enum):
    """數據來源平台"""
    ESOURCES = "esources"
    CREOATE = "creoate"
    THEWHOLESALER = "thewholesaler"
    MANUAL = "manual"
    IMPORT = "import"


class VerificationStatus(enum.Enum):
    """驗證狀態"""
    PENDING = "pending"
    VERIFIED = "verified"
    INVALID = "invalid"
    DUPLICATE = "duplicate"


class Supplier(Base):
    """供應商/潛在客戶模型"""
    
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 基本資訊
    company_name = Column(String(255), nullable=False, index=True)
    website = Column(String(500))
    email = Column(String(255), index=True)
    phone = Column(String(50))
    address = Column(Text)
    country = Column(String(100), index=True)
    city = Column(String(100))
    
    # 業務資訊
    business_type = Column(String(100))  # 批發商、制造商、分銷商等
    product_categories = Column(JSON)  # 產品類別列表
    min_order_quantity = Column(String(100))
    price_range = Column(String(100))
    certifications = Column(JSON)  # 認證列表
    
    # 描述
    description = Column(Text)
    about_us = Column(Text)
    
    # 來源追蹤
    source_platform = Column(Enum(SourcePlatform, values_callable=lambda obj: [e.value for e in obj]), default=SourcePlatform.MANUAL)
    source_url = Column(String(1000))
    source_page_title = Column(String(500))
    
    # 驗證狀態
    verification_status = Column(Enum(VerificationStatus, values_callable=lambda obj: [e.value for e in obj]), default=VerificationStatus.PENDING)
    verification_notes = Column(Text)
    verified_at = Column(DateTime, nullable=True)
    
    # 評分
    quality_score = Column(Float, default=0.0)  # 0-100
    
    # 標籤
    tags = Column(JSON)  # 自定義標籤列表
    
    # 狀態
    is_contacted = Column(Boolean, default=False)
    is_customer = Column(Boolean, default=False)
    is_blacklisted = Column(Boolean, default=False)
    
    # 原始數據（爬蟲獲取）
    raw_data = Column(JSON)
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contacted_at = Column(DateTime, nullable=True)
    
    # 關係
    owner = relationship("User", back_populates="suppliers")
    emails = relationship("Email", back_populates="supplier", cascade="all, delete-orphan")
    activities = relationship("ActivityLog", back_populates="supplier", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Supplier {self.company_name}>"
