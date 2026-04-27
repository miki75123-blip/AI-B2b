"""
儀表板 API 路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.user import User
from app.models.supplier import Supplier, SourcePlatform, VerificationStatus
from app.models.campaign import Campaign, CampaignStatus
from app.models.email import Email, EmailStatus
from app.models.activity_log import ActivityLog
from app.api.auth import get_current_user
from pydantic import BaseModel
from typing import List

router = APIRouter()


class SupplierStats(BaseModel):
    """供應商統計"""
    total: int
    verified: int
    pending: int
    contacted: int
    customers: int
    by_platform: dict


class EmailStats(BaseModel):
    """郵件統計"""
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_bounced: int
    open_rate: float
    click_rate: float


class RecentActivity(BaseModel):
    """最近活動"""
    id: int
    activity_type: str
    title: str
    description: str
    success: bool
    created_at: datetime


class CampaignSummary(BaseModel):
    """活動摘要"""
    id: int
    name: str
    status: str
    emails_sent: int
    open_rate: float
    click_rate: float


class DashboardStats(BaseModel):
    """儀表板統計"""
    supplier_stats: SupplierStats
    email_stats: EmailStats
    campaign_stats: dict
    recent_activities: List[RecentActivity]
    top_campaigns: List[CampaignSummary]


@router.get("/", response_model=DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取儀表板數據"""
    
    # 供應商統計
    total_suppliers = db.query(Supplier).filter(
        Supplier.owner_id == current_user.id
    ).count()
    
    verified_suppliers = db.query(Supplier).filter(
        Supplier.owner_id == current_user.id,
        Supplier.verification_status == VerificationStatus.VERIFIED
    ).count()
    
    pending_suppliers = db.query(Supplier).filter(
        Supplier.owner_id == current_user.id,
        Supplier.verification_status == VerificationStatus.PENDING
    ).count()
    
    contacted_suppliers = db.query(Supplier).filter(
        Supplier.owner_id == current_user.id,
        Supplier.is_contacted == True
    ).count()
    
    customer_suppliers = db.query(Supplier).filter(
        Supplier.owner_id == current_user.id,
        Supplier.is_customer == True
    ).count()
    
    # 按平台統計
    platform_stats = db.query(
        Supplier.source_platform,
        func.count(Supplier.id).label('count')
    ).filter(
        Supplier.owner_id == current_user.id
    ).group_by(Supplier.source_platform).all()
    
    by_platform = {p.value: c for p, c in platform_stats}
    
    supplier_stats = SupplierStats(
        total=total_suppliers,
        verified=verified_suppliers,
        pending=pending_suppliers,
        contacted=contacted_suppliers,
        customers=customer_suppliers,
        by_platform=by_platform
    )
    
    # 郵件統計
    emails = db.query(Email).join(Email.supplier).filter(
        Email.supplier.has(owner_id=current_user.id)
    ).all()
    
    total_sent = len(emails)
    total_delivered = sum(1 for e in emails if e.status not in [EmailStatus.PENDING, EmailStatus.QUEUED, EmailStatus.FAILED])
    total_opened = sum(1 for e in emails if e.status in [EmailStatus.OPENED, EmailStatus.CLICKED])
    total_clicked = sum(1 for e in emails if e.status == EmailStatus.CLICKED)
    total_bounced = sum(1 for e in emails if e.status == EmailStatus.BOUNCED)
    
    email_stats = EmailStats(
        total_sent=total_sent,
        total_delivered=total_delivered,
        total_opened=total_opened,
        total_clicked=total_clicked,
        total_bounced=total_bounced,
        open_rate=round(total_opened / total_sent * 100, 2) if total_sent > 0 else 0,
        click_rate=round(total_clicked / total_sent * 100, 2) if total_sent > 0 else 0,
    )
    
    # 活動統計
    total_campaigns = db.query(Campaign).filter(
        Campaign.owner_id == current_user.id
    ).count()
    
    active_campaigns = db.query(Campaign).filter(
        Campaign.owner_id == current_user.id,
        Campaign.status == CampaignStatus.RUNNING
    ).count()
    
    campaign_stats = {
        "total": total_campaigns,
        "active": active_campaigns
    }
    
    # 最近活動
    recent_activities_query = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id
    ).order_by(ActivityLog.created_at.desc()).limit(10).all()
    
    recent_activities = [
        RecentActivity(
            id=a.id,
            activity_type=a.activity_type.value,
            title=a.title,
            description=a.description or "",
            success=a.success,
            created_at=a.created_at
        ) for a in recent_activities_query
    ]
    
    # 表現最好的活動
    top_campaigns_query = db.query(Campaign).filter(
        Campaign.owner_id == current_user.id,
        Campaign.emails_sent > 0
    ).order_by(Campaign.emails_opened.desc()).limit(5).all()
    
    top_campaigns = [
        CampaignSummary(
            id=c.id,
            name=c.name,
            status=c.status.value,
            emails_sent=c.emails_sent,
            open_rate=c.open_rate,
            click_rate=c.click_rate
        ) for c in top_campaigns_query
    ]
    
    return DashboardStats(
        supplier_stats=supplier_stats,
        email_stats=email_stats,
        campaign_stats=campaign_stats,
        recent_activities=recent_activities,
        top_campaigns=top_campaigns
    )


@router.get("/suppliers/by-country")
def get_suppliers_by_country(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """按國家分組的供應商數量"""
    results = db.query(
        Supplier.country,
        func.count(Supplier.id).label('count')
    ).filter(
        Supplier.owner_id == current_user.id,
        Supplier.country.isnot(None)
    ).group_by(Supplier.country).all()
    
    return [{"country": r[0] or "Unknown", "count": r[1]} for r in results]


@router.get("/emails/timeline")
def get_email_timeline(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """郵件發送時間線"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        func.date(Email.sent_at).label('date'),
        func.count(Email.id).label('sent'),
        func.sum(func.cast(Email.status == EmailStatus.OPENED, Integer)).label('opened'),
    ).join(Email.supplier).filter(
        Email.supplier.has(owner_id=current_user.id),
        Email.sent_at >= start_date
    ).group_by(func.date(Email.sent_at)).all()
    
    return [
        {"date": str(r[0]), "sent": r[1], "opened": r[2] or 0}
        for r in results
    ]
