"""
營銷活動 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.models.campaign import Campaign, CampaignStatus
from app.models.activity_log import ActivityLog, ActivityType
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignStats
)
from app.api.auth import get_current_user
from app.tasks.campaign_tasks import run_campaign_task, pause_campaign_task

router = APIRouter()


def campaign_to_response(campaign: Campaign) -> CampaignResponse:
    """將 Campaign 模型轉換為響應 Schema"""
    return CampaignResponse(
        id=campaign.id,
        owner_id=campaign.owner_id,
        name=campaign.name,
        description=campaign.description,
        target_countries=campaign.target_countries,
        target_business_types=campaign.target_business_types,
        target_product_categories=campaign.target_product_categories,
        email_template_id=campaign.email_template_id,
        daily_send_limit=campaign.daily_send_limit,
        total_send_limit=campaign.total_send_limit,
        emails_sent=campaign.emails_sent,
        emails_opened=campaign.emails_opened,
        emails_clicked=campaign.emails_clicked,
        emails_bounced=campaign.emails_bounced,
        unsubscribes=campaign.unsubscribes,
        status=campaign.status,
        open_rate=campaign.open_rate,
        click_rate=campaign.click_rate,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        started_at=campaign.started_at,
        completed_at=campaign.completed_at,
        last_run_at=campaign.last_run_at,
    )


@router.get("/", response_model=List[CampaignResponse])
def list_campaigns(
    skip: int = 0,
    limit: int = 100,
    status: Optional[CampaignStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """列出營銷活動"""
    query = db.query(Campaign).filter(Campaign.owner_id == current_user.id)
    
    if status:
        query = query.filter(Campaign.status == status)
    
    campaigns = query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit).all()
    return [campaign_to_response(c) for c in campaigns]


@router.get("/stats", response_model=CampaignStats)
def get_campaign_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取活動統計"""
    campaigns = db.query(Campaign).filter(Campaign.owner_id == current_user.id).all()
    
    total_sent = sum(c.emails_sent for c in campaigns)
    total_opened = sum(c.emails_opened for c in campaigns)
    total_clicked = sum(c.emails_clicked for c in campaigns)
    
    return CampaignStats(
        total_campaigns=len(campaigns),
        active_campaigns=sum(1 for c in campaigns if c.status == CampaignStatus.RUNNING),
        total_sent=total_sent,
        total_opened=total_opened,
        total_clicked=total_clicked,
        overall_open_rate=round(total_opened / total_sent * 100, 2) if total_sent > 0 else 0,
        overall_click_rate=round(total_clicked / total_sent * 100, 2) if total_sent > 0 else 0,
    )


@router.post("/", response_model=CampaignResponse)
def create_campaign(
    campaign_data: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """創建營銷活動"""
    campaign = Campaign(
        owner_id=current_user.id,
        **campaign_data.model_dump()
    )
    
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    # 記錄活動
    log = ActivityLog(
        user_id=current_user.id,
        campaign_id=campaign.id,
        activity_type=ActivityType.CAMPAIGN_CREATED,
        title="創建活動",
        description=f"創建了新活動: {campaign.name}",
        success=True,
    )
    db.add(log)
    db.commit()
    
    return campaign_to_response(campaign)


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取活動詳情"""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.owner_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活動不存在"
        )
    
    return campaign_to_response(campaign)


@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新營銷活動"""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.owner_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活動不存在"
        )
    
    if campaign.status == CampaignStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="運行中的活動無法修改"
        )
    
    update_data = campaign_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    db.commit()
    db.refresh(campaign)
    
    return campaign_to_response(campaign)


@router.delete("/{campaign_id}")
def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """刪除營銷活動"""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.owner_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活動不存在"
        )
    
    if campaign.status == CampaignStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="運行中的活動無法刪除"
        )
    
    db.delete(campaign)
    db.commit()
    
    return {"message": "活動已刪除"}


@router.post("/{campaign_id}/start")
def start_campaign(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """啟動活動"""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.owner_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活動不存在"
        )
    
    if campaign.status != CampaignStatus.DRAFT and campaign.status != CampaignStatus.PAUSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="活動無法啟動"
        )
    
    campaign.status = CampaignStatus.RUNNING
    campaign.started_at = datetime.utcnow()
    db.commit()
    
    # 記錄活動
    log = ActivityLog(
        user_id=current_user.id,
        campaign_id=campaign.id,
        activity_type=ActivityType.CAMPAIGN_STARTED,
        title="啟動活動",
        description=f"活動已啟動: {campaign.name}",
        success=True,
    )
    db.add(log)
    db.commit()
    
    # 觸發 Celery 任務
    run_campaign_task.delay(campaign.id)
    
    return {"message": "活動已啟動", "campaign_id": campaign.id}


@router.post("/{campaign_id}/pause")
def pause_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """暫停活動"""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.owner_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活動不存在"
        )
    
    if campaign.status != CampaignStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有運行中的活動可以暫停"
        )
    
    campaign.status = CampaignStatus.PAUSED
    db.commit()
    
    # 記錄活動
    log = ActivityLog(
        user_id=current_user.id,
        campaign_id=campaign.id,
        activity_type=ActivityType.CAMPAIGN_PAUSED,
        title="暫停活動",
        description=f"活動已暫停: {campaign.name}",
        success=True,
    )
    db.add(log)
    db.commit()
    
    # 通知 Celery Worker
    pause_campaign_task.delay(campaign.id)
    
    return {"message": "活動已暫停", "campaign_id": campaign.id}


@router.post("/{campaign_id}/stop")
def stop_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """停止活動"""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.owner_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活動不存在"
        )
    
    campaign.status = CampaignStatus.COMPLETED
    campaign.completed_at = datetime.utcnow()
    db.commit()
    
    # 記錄活動
    log = ActivityLog(
        user_id=current_user.id,
        campaign_id=campaign.id,
        activity_type=ActivityType.CAMPAIGN_COMPLETED,
        title="停止活動",
        description=f"活動已停止: {campaign.name}",
        success=True,
    )
    db.add(log)
    db.commit()
    
    return {"message": "活動已停止", "campaign_id": campaign.id}
