"""
活動日誌模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class ActivityType(enum.Enum):
    """活動類型"""
    # 供應商相關
    SUPPLIER_CREATED = "supplier_created"
    SUPPLIER_UPDATED = "supplier_updated"
    SUPPLIER_IMPORTED = "supplier_imported"
    SUPPLIER_SCRAPED = "supplier_scraped"
    SUPPLIER_VERIFIED = "supplier_verified"
    SUPPLIER_BLACKLISTED = "supplier_blacklisted"
    
    # 郵件相關
    EMAIL_QUEUED = "email_queued"
    EMAIL_SENT = "email_sent"
    EMAIL_DELIVERED = "email_delivered"
    EMAIL_OPENED = "email_opened"
    EMAIL_CLICKED = "email_clicked"
    EMAIL_BOUNCED = "email_bounced"
    EMAIL_FAILED = "email_failed"
    EMAIL_UNSUBSCRIBED = "email_unsubscribed"
    
    # 活動相關
    CAMPAIGN_CREATED = "campaign_created"
    CAMPAIGN_STARTED = "campaign_started"
    CAMPAIGN_PAUSED = "campaign_paused"
    CAMPAIGN_COMPLETED = "campaign_completed"
    
    # 系統相關
    AGENT_RUN = "agent_run"
    SYSTEM_ERROR = "system_error"
    OPTIMIZATION_APPLIED = "optimization_applied"


class ActivityLog(Base):
    """活動日誌模型"""
    
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), index=True, nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), index=True, nullable=True)
    email_id = Column(Integer, ForeignKey("emails.id"), index=True, nullable=True)
    
    # 活動類型
    activity_type = Column(Enum(ActivityType), nullable=False, index=True)
    
    # 詳情
    title = Column(String(255), nullable=False)
    description = Column(Text)
    log_metadata = Column(JSON)  # 額外元數據（改名避免衝突）
    
    # 狀態
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 關係
    user = relationship("User", back_populates="activity_logs")
    supplier = relationship("Supplier", back_populates="activities")
    
    def __repr__(self):
        return f"<ActivityLog {self.activity_type.value} - {self.created_at}>"
