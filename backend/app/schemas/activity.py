"""
活動日誌 Pydantic Schema
"""
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class ActivityType(str, Enum):
    """活動類型"""
    SUPPLIER_CREATED = "supplier_created"
    SUPPLIER_UPDATED = "supplier_updated"
    SUPPLIER_IMPORTED = "supplier_imported"
    SUPPLIER_SCRAPED = "supplier_scraped"
    SUPPLIER_VERIFIED = "supplier_verified"
    SUPPLIER_BLACKLISTED = "supplier_blacklisted"
    EMAIL_QUEUED = "email_queued"
    EMAIL_SENT = "email_sent"
    EMAIL_DELIVERED = "email_delivered"
    EMAIL_OPENED = "email_opened"
    EMAIL_CLICKED = "email_clicked"
    EMAIL_BOUNCED = "email_bounced"
    EMAIL_FAILED = "email_failed"
    EMAIL_UNSUBSCRIBED = "email_unsubscribed"
    CAMPAIGN_CREATED = "campaign_created"
    CAMPAIGN_STARTED = "campaign_started"
    CAMPAIGN_PAUSED = "campaign_paused"
    CAMPAIGN_COMPLETED = "campaign_completed"
    AGENT_RUN = "agent_run"
    SYSTEM_ERROR = "system_error"
    OPTIMIZATION_APPLIED = "optimization_applied"


class ActivityLogResponse(BaseModel):
    """活動日誌響應 Schema"""
    id: int
    user_id: Optional[int]
    supplier_id: Optional[int]
    campaign_id: Optional[int]
    email_id: Optional[int]
    activity_type: ActivityType
    title: str
    description: Optional[str]
    metadata: Optional[dict]
    success: bool
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ActivityLogList(BaseModel):
    """活動日誌列表響應"""
    items: List[ActivityLogResponse]
    total: int
    page: int
    page_size: int
