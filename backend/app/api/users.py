"""
用戶 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.activity_log import ActivityLog, ActivityType
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.activity import ActivityLogResponse
from app.api.auth import get_current_user
from typing import List
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """列出所有用戶（僅管理員）"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理員權限"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """獲取個人資料"""
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新個人資料"""
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.put("/password")
def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """修改密碼"""
    from app.core.security import verify_password
    
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密碼錯誤"
        )
    
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密碼至少需要 8 個字符"
        )
    
    current_user.hashed_password = get_password_hash(new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "密碼修改成功"}


@router.post("/settings", response_model=UserResponse)
def update_settings(
    sendgrid_api_key: str = None,
    email_from_address: str = None,
    email_from_name: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新郵件設置"""
    if sendgrid_api_key is not None:
        current_user.sendgrid_api_key = sendgrid_api_key
    if email_from_address is not None:
        current_user.email_from_address = email_from_address
    if email_from_name is not None:
        current_user.email_from_name = email_from_name
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    # 記錄活動
    log = ActivityLog(
        user_id=current_user.id,
        activity_type=ActivityType.SYSTEM_ERROR,  # 借用類型
        title="更新郵件設置",
        description="用戶更新了 SendGrid 郵件配置",
        success=True,
    )
    db.add(log)
    db.commit()
    
    return current_user
