"""
郵件服務
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.supplier import Supplier
from app.models.email import Email, EmailTemplate, EmailStatus
from app.models.campaign import Campaign, CampaignStatus
from app.agents.writer_agent import WriterAgent
from app.agents.sender_agent import SenderAgent
from loguru import logger


class EmailService:
    """郵件服務"""
    
    def __init__(self, user_id: int, db: Session):
        self.user_id = user_id
        self.db = db
        self.user = db.query(User).filter(User.id == user_id).first()
        self.writer = WriterAgent(user_id, db)
        self.sender = SenderAgent(user_id, db)
    
    def create_email(
        self,
        campaign_id: int,
        supplier_id: int,
        use_ab_test: bool = False
    ) -> Optional[Email]:
        """
        創建並排隊郵件
        
        Args:
            campaign_id: 活動 ID
            supplier_id: 供應商 ID
            use_ab_test: 是否使用 A/B 測試
            
        Returns:
            創建的郵件對象或 None
        """
        campaign = self.db.query(Campaign).filter(
            Campaign.id == campaign_id,
            Campaign.owner_id == self.user_id
        ).first()
        
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found")
            return None
        
        supplier = self.db.query(Supplier).filter(
            Supplier.id == supplier_id,
            Supplier.owner_id == self.user_id
        ).first()
        
        if not supplier:
            logger.error(f"Supplier {supplier_id} not found")
            return None
        
        template = self.db.query(EmailTemplate).filter(
            EmailTemplate.id == campaign.email_template_id
        ).first()
        
        if not template:
            logger.error(f"Template {campaign.email_template_id} not found")
            return None
        
        # 生成個性化郵件
        email_content = self.writer.generate_personalized_email(
            template=template,
            supplier=supplier,
            campaign=campaign
        )
        
        # 創建郵件記錄
        email_record = Email(
            campaign_id=campaign_id,
            supplier_id=supplier_id,
            to_email=supplier.email,
            to_name=supplier.company_name,
            from_email=self.user.email_from_address or self.user.email,
            from_name=self.user.email_from_name or self.user.full_name,
            subject=email_content["subject"],
            body_html=email_content["body"],
            body_text=email_content["body_text"],
            status=EmailStatus.PENDING,
            ab_variant="B" if use_ab_test else "A"
        )
        
        self.db.add(email_record)
        
        # 更新模板使用次數
        template.usage_count += 1
        
        # 更新供應商狀態
        supplier.is_contacted = True
        supplier.last_contacted_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(email_record)
        
        return email_record
    
    def send_email(self, email_id: int) -> Dict[str, Any]:
        """
        發送郵件
        
        Args:
            email_id: 郵件 ID
            
        Returns:
            發送結果
        """
        email_record = self.db.query(Email).filter(
            Email.id == email_id
        ).first()
        
        if not email_record:
            return {"error": "Email not found"}
        
        result = self.sender.send_email(
            email_record=email_record,
            sendgrid_api_key=self.user.sendgrid_api_key,
            from_email=self.user.email_from_address or self.user.email,
            from_name=self.user.email_from_name or self.user.full_name
        )
        
        if result["success"]:
            email_record.status = EmailStatus.SENT
            email_record.sent_at = datetime.utcnow()
            email_record.sendgrid_message_id = result.get("message_id")
            
            # 更新活動統計
            campaign = self.db.query(Campaign).filter(
                Campaign.id == email_record.campaign_id
            ).first()
            if campaign:
                campaign.emails_sent += 1
        else:
            email_record.status = EmailStatus.FAILED
            email_record.error_message = result.get("error")
        
        self.db.commit()
        
        return result
    
    def queue_campaign_emails(
        self,
        campaign_id: int,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        為活動排隊郵件
        
        Args:
            campaign_id: 活動 ID
            limit: 限制數量
            
        Returns:
            排隊結果
        """
        campaign = self.db.query(Campaign).filter(
            Campaign.id == campaign_id,
            Campaign.owner_id == self.user_id
        ).first()
        
        if not campaign:
            return {"error": "Campaign not found"}
        
        # 構建查詢
        query = self.db.query(Supplier).filter(
            Supplier.owner_id == self.user_id,
            Supplier.verification_status.value == "verified",
            Supplier.is_contacted == False,
            Supplier.is_blacklisted == False,
            Supplier.email.isnot(None)
        )
        
        # 應用活動目標過濾
        if campaign.target_countries:
            query = query.filter(Supplier.country.in_(campaign.target_countries))
        if campaign.target_business_types:
            query = query.filter(Supplier.business_type.in_(campaign.target_business_types))
        
        # 計算剩餘配額
        remaining = campaign.total_send_limit - campaign.emails_sent
        actual_limit = min(remaining, limit, campaign.daily_send_limit)
        
        suppliers = query.limit(actual_limit).all()
        
        queued = 0
        for supplier in suppliers:
            email = self.create_email(campaign_id, supplier.id)
            if email:
                queued += 1
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "queued": queued,
            "remaining_quota": remaining - queued
        }
    
    def get_email_stats(self, campaign_id: int = None) -> Dict[str, Any]:
        """
        獲取郵件統計
        
        Args:
            campaign_id: 可選的活動 ID
            
        Returns:
            統計數據
        """
        query = self.db.query(Email).join(Email.supplier).filter(
            Email.supplier.has(owner_id=self.user_id)
        )
        
        if campaign_id:
            query = query.filter(Email.campaign_id == campaign_id)
        
        emails = query.all()
        
        total = len(emails)
        sent = sum(1 for e in emails if e.status not in [EmailStatus.PENDING, EmailStatus.QUEUED])
        delivered = sum(1 for e in emails if e.status in [
            EmailStatus.DELIVERED, EmailStatus.OPENED, EmailStatus.CLICKED
        ])
        opened = sum(1 for e in emails if e.status in [
            EmailStatus.OPENED, EmailStatus.CLICKED
        ])
        clicked = sum(1 for e in emails if e.status == EmailStatus.CLICKED)
        bounced = sum(1 for e in emails if e.status == EmailStatus.BOUNCED)
        failed = sum(1 for e in emails if e.status == EmailStatus.FAILED)
        
        return {
            "total": total,
            "sent": sent,
            "delivered": delivered,
            "opened": opened,
            "clicked": clicked,
            "bounced": bounced,
            "failed": failed,
            "delivery_rate": round(delivered / sent * 100, 2) if sent > 0 else 0,
            "open_rate": round(opened / delivered * 100, 2) if delivered > 0 else 0,
            "click_rate": round(clicked / delivered * 100, 2) if delivered > 0 else 0,
        }
