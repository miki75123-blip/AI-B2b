"""
活動日誌 API 路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.activity_log import ActivityLog, ActivityType
from app.schemas.activity import ActivityLogResponse, ActivityLogList
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=ActivityLogList)
def list_activities(
    page: int = 1,
    page_size: int = 50,
    activity_type: Optional[ActivityType] = None,
    supplier_id: Optional[int] = None,
    campaign_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """列出活動日誌"""
    query = db.query(ActivityLog).filter(ActivityLog.user_id == current_user.id)
    
    if activity_type:
        query = query.filter(ActivityLog.activity_type == activity_type)
    if supplier_id:
        query = query.filter(ActivityLog.supplier_id == supplier_id)
    if campaign_id:
        query = query.filter(ActivityLog.campaign_id == campaign_id)
    
    total = query.count()
    offset = (page - 1) * page_size
    
    activities = query.order_by(ActivityLog.created_at.desc()).offset(offset).limit(page_size).all()
    
    return ActivityLogList(
        items=activities,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{activity_id}", response_model=ActivityLogResponse)
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取活動詳情"""
    activity = db.query(ActivityLog).filter(
        ActivityLog.id == activity_id,
        ActivityLog.user_id == current_user.id
    ).first()
    
    if not activity:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活動日誌不存在"
        )
    
    return activity
