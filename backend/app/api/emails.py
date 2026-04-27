"""
郵件 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.models.email import Email, EmailTemplate, EmailStatus
from app.schemas.email import (
    EmailTemplateCreate, EmailTemplateUpdate, EmailTemplateResponse, EmailResponse
)
from app.api.auth import get_current_user
from app.tasks.email_tasks import send_email_task, batch_send_emails_task

router = APIRouter()


@router.get("/templates", response_model=List[EmailTemplateResponse])
def list_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """列出郵件模板"""
    templates = db.query(EmailTemplate).filter(
        EmailTemplate.owner_id == current_user.id
    ).order_by(EmailTemplate.created_at.desc()).offset(skip).limit(limit).all()
    
    return templates


@router.post("/templates", response_model=EmailTemplateResponse)
def create_template(
    template_data: EmailTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """創建郵件模板"""
    # 如果設為默認，先取消其他默認
    if template_data.is_default:
        db.query(EmailTemplate).filter(
            EmailTemplate.owner_id == current_user.id,
            EmailTemplate.is_default == True
        ).update({"is_default": False})
    
    template = EmailTemplate(
        owner_id=current_user.id,
        **template_data.model_dump()
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return template


@router.get("/templates/{template_id}", response_model=EmailTemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取模板詳情"""
    template = db.query(EmailTemplate).filter(
        EmailTemplate.id == template_id,
        EmailTemplate.owner_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )
    
    return template


@router.put("/templates/{template_id}", response_model=EmailTemplateResponse)
def update_template(
    template_id: int,
    template_data: EmailTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新郵件模板"""
    template = db.query(EmailTemplate).filter(
        EmailTemplate.id == template_id,
        EmailTemplate.owner_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )
    
    update_data = template_data.model_dump(exclude_unset=True)
    
    # 如果設為默認，先取消其他默認
    if update_data.get("is_default"):
        db.query(EmailTemplate).filter(
            EmailTemplate.owner_id == current_user.id,
            EmailTemplate.is_default == True,
            EmailTemplate.id != template_id
        ).update({"is_default": False})
    
    for field, value in update_data.items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    
    return template


@router.delete("/templates/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """刪除郵件模板"""
    template = db.query(EmailTemplate).filter(
        EmailTemplate.id == template_id,
        EmailTemplate.owner_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )
    
    db.delete(template)
    db.commit()
    
    return {"message": "模板已刪除"}


@router.get("/emails", response_model=List[EmailResponse])
def list_emails(
    skip: int = 0,
    limit: int = 100,
    campaign_id: Optional[int] = None,
    status: Optional[EmailStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """列出郵件"""
    query = db.query(Email).join(
        Email.supplier
    ).filter(
        Email.supplier.has(owner_id=current_user.id)
    )
    
    if campaign_id:
        query = query.filter(Email.campaign_id == campaign_id)
    if status:
        query = query.filter(Email.status == status)
    
    emails = query.order_by(Email.created_at.desc()).offset(skip).limit(limit).all()
    return emails


@router.get("/emails/{email_id}", response_model=EmailResponse)
def get_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取郵件詳情"""
    email = db.query(Email).join(
        Email.supplier
    ).filter(
        Email.id == email_id,
        Email.supplier.has(owner_id=current_user.id)
    ).first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="郵件不存在"
        )
    
    return email


@router.post("/send")
def send_single_email(
    supplier_id: int,
    subject: str,
    body: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """發送單封郵件"""
    from app.models.supplier import Supplier
    
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.owner_id == current_user.id
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供應商不存在"
        )
    
    if not supplier.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="供應商沒有郵箱地址"
        )
    
    # 創建郵件記錄
    email = Email(
        supplier_id=supplier_id,
        to_email=supplier.email,
        to_name=supplier.company_name,
        from_email=current_user.email_from_address or current_user.email,
        from_name=current_user.email_from_name or current_user.full_name,
        subject=subject,
        body_html=body,
        status=EmailStatus.PENDING,
    )
    
    db.add(email)
    db.commit()
    db.refresh(email)
    
    # 觸發發送任務
    send_email_task.delay(email.id, current_user.id)
    
    return {"message": "郵件已排隊", "email_id": email.id}
