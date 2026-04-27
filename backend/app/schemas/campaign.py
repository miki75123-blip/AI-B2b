"""
營銷活動 Pydantic Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CampaignStatus(str, Enum):
    """活動狀態"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignBase(BaseModel):
    """活動基礎 Schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    target_countries: Optional[List[str]] = None
    target_business_types: Optional[List[str]] = None
    target_product_categories: Optional[List[str]] = None
    email_template_id: Optional[int] = None
    daily_send_limit: int = Field(default=50, ge=1, le=1000)
    total_send_limit: int = Field(default=1000, ge=1)


class CampaignCreate(CampaignBase):
    """活動創建 Schema"""
    pass


class CampaignUpdate(BaseModel):
    """活動更新 Schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    target_countries: Optional[List[str]] = None
    target_business_types: Optional[List[str]] = None
    target_product_categories: Optional[List[str]] = None
    email_template_id: Optional[int] = None
    daily_send_limit: Optional[int] = None
    total_send_limit: Optional[int] = None
    status: Optional[CampaignStatus] = None


class CampaignResponse(CampaignBase):
    """活動響應 Schema"""
    id: int
    owner_id: int
    status: CampaignStatus
    emails_sent: int
    emails_opened: int
    emails_clicked: int
    emails_bounced: int
    unsubscribes: int
    open_rate: float
    click_rate: float
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    last_run_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CampaignStats(BaseModel):
    """活動統計 Schema"""
    total_campaigns: int
    active_campaigns: int
    total_sent: int
    total_opened: int
    total_clicked: int
    overall_open_rate: float
    overall_click_rate: float
