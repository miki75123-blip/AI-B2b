"""
營銷活動模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class CampaignStatus(enum.Enum):
    """活動狀態"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Campaign(Base):
    """營銷活動模型"""
    
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 基本資訊
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # 配置
    target_countries = Column(JSON)  # 目標國家列表
    target_business_types = Column(JSON)  # 目標企業類型
    target_product_categories = Column(JSON)  # 目標產品類別
    
    # 郵件配置
    email_template_id = Column(Integer, ForeignKey("email_templates.id"), nullable=True)
    
    # 限制
    daily_send_limit = Column(Integer, default=50)
    total_send_limit = Column(Integer, default=1000)
    
    # 統計
    emails_sent = Column(Integer, default=0)
    emails_opened = Column(Integer, default=0)
    emails_clicked = Column(Integer, default=0)
    emails_bounced = Column(Integer, default=0)
    unsubscribes = Column(Integer, default=0)
    
    # 狀態
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    
    # 關係
    owner = relationship("User", back_populates="campaigns")
    email_template = relationship("EmailTemplate", foreign_keys=[email_template_id])
    emails = relationship("Email", back_populates="campaign", cascade="all, delete-orphan")
    
    @property
    def open_rate(self) -> float:
        """開啟率"""
        if self.emails_sent == 0:
            return 0.0
        return round(self.emails_opened / self.emails_sent * 100, 2)
    
    @property
    def click_rate(self) -> float:
        """點擊率"""
        if self.emails_sent == 0:
            return 0.0
        return round(self.emails_clicked / self.emails_sent * 100, 2)
    
    def __repr__(self):
        return f"<Campaign {self.name}>"
