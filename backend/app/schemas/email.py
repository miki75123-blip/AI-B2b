"""
郵件 Pydantic Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EmailStatus(str, Enum):
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


class EmailTemplateBase(BaseModel):
    """郵件模板基礎 Schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    subject_template: str = Field(..., min_length=1, max_length=500)
    body_template: str = Field(..., min_length=10)
    variables: Optional[str] = None
    ab_test_enabled: bool = False
    variant_b_subject: Optional[str] = None
    variant_b_body: Optional[str] = None


class EmailTemplateCreate(EmailTemplateBase):
    """郵件模板創建 Schema"""
    is_default: bool = False


class EmailTemplateUpdate(BaseModel):
    """郵件模板更新 Schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    subject_template: Optional[str] = None
    body_template: Optional[str] = None
    variables: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    ab_test_enabled: Optional[bool] = None
    variant_b_subject: Optional[str] = None
    variant_b_body: Optional[str] = None


class EmailTemplateResponse(EmailTemplateBase):
    """郵件模板響應 Schema"""
    id: int
    owner_id: int
    is_active: bool
    is_default: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmailResponse(BaseModel):
    """郵件響應 Schema"""
    id: int
    campaign_id: Optional[int]
    supplier_id: Optional[int]
    to_email: str
    to_name: Optional[str]
    subject: str
    status: EmailStatus
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    opened_at: Optional[datetime]
    clicked_at: Optional[datetime]
    open_count: int
    click_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmailQueueRequest(BaseModel):
    """郵件排隊請求"""
    campaign_id: int
    supplier_ids: List[int]
