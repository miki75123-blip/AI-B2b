"""
郵件模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class EmailStatus(enum.Enum):
    """郵件狀態"""
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    FAILED = "failed"
    UNSUBSCRIBED = "unsubscribed"


class Email(Base):
    """郵件記錄模型"""
    
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), index=True)
    
    # 收件人
    to_email = Column(String(255), nullable=False)
    to_name = Column(String(200))
    
    # 發件人
    from_email = Column(String(255))
    from_name = Column(String(200))
    
    # 郵件內容
    subject = Column(String(500), nullable=False)
    body_html = Column(Text)
    body_text = Column(Text)
    
    # SendGrid 追蹤
    sendgrid_message_id = Column(String(255))
    
    # 狀態追蹤
    status = Column(Enum(EmailStatus), default=EmailStatus.PENDING)
    
    # 互動追蹤
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    
    # 打開次數
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    
    # 錯誤資訊
    error_message = Column(Text)
    
    # A/B 測試
    ab_variant = Column(String(10))  # A 或 B
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關係
    campaign = relationship("Campaign", back_populates="emails")
    supplier = relationship("Supplier", back_populates="emails")
    
    def __repr__(self):
        return f"<Email {self.to_email} - {self.status.value}>"


class EmailTemplate(Base):
    """郵件模板模型"""
    
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 基本資訊
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # 模板內容
    subject_template = Column(String(500), nullable=False)
    body_template = Column(Text, nullable=False)
    
    # 變量說明
    variables = Column(Text)  # JSON 字串，列出可用變量
    
    # 狀態
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # A/B 測試
    ab_test_enabled = Column(Boolean, default=False)
    variant_b_subject = Column(String(500))
    variant_b_body = Column(Text)
    
    # 使用統計
    usage_count = Column(Integer, default=0)
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關係
    owner = relationship("User", back_populates="email_templates")
    campaigns = relationship("Campaign", back_populates="email_template")
    
    def __repr__(self):
        return f"<EmailTemplate {self.name}>"
