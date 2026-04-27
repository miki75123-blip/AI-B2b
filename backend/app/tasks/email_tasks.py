"""
郵件發送任務
"""
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.user import User
from app.models.supplier import Supplier
from app.models.email import Email, EmailTemplate, EmailStatus
from app.models.campaign import Campaign, CampaignStatus
from app.models.activity_log import ActivityLog, ActivityType
from app.agents.sender_agent import SenderAgent
from app.agents.writer_agent import WriterAgent
from loguru import logger
from datetime import datetime
import traceback


@celery_app.task(bind=True, max_retries=3)
def send_email_task(self, email_id: int, user_id: int):
    """
    發送單封郵件任務
    
    Args:
        email_id: 郵件記錄 ID
        user_id: 用戶 ID
    """
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {"error": "User not found"}
        
        email_record = db.query(Email).filter(Email.id == email_id).first()
        if not email_record:
            return {"error": "Email not found"}
        
        # 創建 Sender Agent
        sender = SenderAgent(user_id, db)
        
        # 發送郵件
        result = sender.send_email(
            email_record=email_record,
            sendgrid_api_key=user.sendgrid_api_key,
            from_email=user.email_from_address or user.email,
            from_name=user.email_from_name or user.full_name
        )
        
        if result["success"]:
            email_record.status = EmailStatus.SENT
            email_record.sent_at = datetime.utcnow()
            email_record.sendgrid_message_id = result.get("message_id")
            
            log = ActivityLog(
                user_id=user_id,
                email_id=email_id,
                activity_type=ActivityType.EMAIL_SENT,
                title="郵件已發送",
                description=f"郵件已發送至 {email_record.to_email}",
                success=True,
            )
        else:
            email_record.status = EmailStatus.FAILED
            email_record.error_message = result.get("error")
            
            log = ActivityLog(
                user_id=user_id,
                email_id=email_id,
                activity_type=ActivityType.EMAIL_FAILED,
                title="郵件發送失敗",
                description=f"郵件發送失敗: {result.get('error')}",
                success=False,
                error_message=result.get("error"),
            )
        
        db.add(log)
        db.commit()
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending email {email_id}: {str(e)}")
        
        log = ActivityLog(
            user_id=user_id,
            email_id=email_id,
            activity_type=ActivityType.EMAIL_FAILED,
            title="郵件發送失敗",
            description=f"郵件發送異常: {str(e)}",
            success=False,
            error_message=traceback.format_exc(),
        )
        db.add(log)
        db.commit()
        
        raise self.retry(exc=e, countdown=60)
        
    finally:
        db.close()


@celery_app.task
def batch_send_emails_task(campaign_id: int):
    """
    批量發送郵件任務
    
    Args:
        campaign_id: 活動 ID
    """
    db = SessionLocal()
    
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return {"error": "Campaign not found"}
        
        if campaign.status != CampaignStatus.RUNNING:
            return {"error": "Campaign is not running"}
        
        user = db.query(User).filter(User.id == campaign.owner_id).first()
        
        # 創建 Sender Agent
        sender = SenderAgent(campaign.owner_id, db)
        writer = WriterAgent(campaign.owner_id, db)
        
        # 獲取目標供應商
        query = db.query(Supplier).filter(
            Supplier.owner_id == campaign.owner_id,
            Supplier.verification_status.value == "verified",
            Supplier.is_contacted == False,
            Supplier.is_blacklisted == False,
            Supplier.email.isnot(None)
        )
        
        # 按國家過濾
        if campaign.target_countries:
            query = query.filter(Supplier.country.in_(campaign.target_countries))
        
        # 按企業類型過濾
        if campaign.target_business_types:
            query = query.filter(Supplier.business_type.in_(campaign.target_business_types))
        
        # 限制數量
        remaining = campaign.total_send_limit - campaign.emails_sent
        suppliers = query.limit(min(remaining, campaign.daily_send_limit)).all()
        
        # 獲取模板
        template = db.query(EmailTemplate).filter(
            EmailTemplate.id == campaign.email_template_id
        ).first()
        
        if not template:
            return {"error": "Email template not found"}
        
        sent_count = 0
        failed_count = 0
        
        for supplier in suppliers:
            # 生成個性化郵件
            email_content = writer.generate_personalized_email(
                template=template,
                supplier=supplier,
                campaign=campaign
            )
            
            # 創建郵件記錄
            email_record = Email(
                campaign_id=campaign_id,
                supplier_id=supplier.id,
                to_email=supplier.email,
                to_name=supplier.company_name,
                from_email=user.email_from_address or user.email,
                from_name=user.email_from_name or user.full_name,
                subject=email_content["subject"],
                body_html=email_content["body"],
                body_text=email_content["body_text"],
                status=EmailStatus.QUEUED,
            )
            db.add(email_record)
            
            # 發送郵件
            result = sender.send_email(
                email_record=email_record,
                sendgrid_api_key=user.sendgrid_api_key,
                from_email=user.email_from_address or user.email,
                from_name=user.email_from_name or user.full_name
            )
            
            if result["success"]:
                email_record.status = EmailStatus.SENT
                email_record.sent_at = datetime.utcnow()
                email_record.sendgrid_message_id = result.get("message_id")
                sent_count += 1
                
                # 更新供應商狀態
                supplier.is_contacted = True
                supplier.last_contacted_at = datetime.utcnow()
            else:
                email_record.status = EmailStatus.FAILED
                email_record.error_message = result.get("error")
                failed_count += 1
        
        # 更新活動統計
        campaign.emails_sent += sent_count
        campaign.last_run_at = datetime.utcnow()
        
        # 檢查是否完成
        if campaign.emails_sent >= campaign.total_send_limit:
            campaign.status = CampaignStatus.COMPLETED
            campaign.completed_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Campaign {campaign_id}: Sent {sent_count} emails, {failed_count} failed")
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "sent": sent_count,
            "failed": failed_count,
            "total_sent": campaign.emails_sent
        }
        
    except Exception as e:
        logger.error(f"Error batch sending emails for campaign {campaign_id}: {str(e)}")
        return {"error": str(e)}
        
    finally:
        db.close()


@celery_app.task
def process_webhook_task(event_data: dict):
    """
    處理 SendGrid Webhook 任務
    
    Args:
        event_data: Webhook 事件數據
    """
    db = SessionLocal()
    
    try:
        event_type = event_data.get("event")
        message_id = event_data.get("sg_message_id")
        
        # 查找郵件記錄
        email_record = db.query(Email).filter(
            Email.sendgrid_message_id.contains(message_id.split('.')[0])
        ).first()
        
        if not email_record:
            logger.warning(f"Email not found for message_id: {message_id}")
            return {"error": "Email not found"}
        
        user_id = email_record.supplier.owner_id if email_record.supplier else None
        
        # 根據事件類型更新狀態
        if event_type == "delivered":
            email_record.status = EmailStatus.DELIVERED
            email_record.delivered_at = datetime.utcnow()
            
        elif event_type == "open":
            email_record.status = EmailStatus.OPENED
            email_record.opened_at = datetime.utcnow()
            email_record.open_count += 1
            
            # 更新活動統計
            if email_record.campaign_id:
                campaign = db.query(Campaign).filter(Campaign.id == email_record.campaign_id).first()
                if campaign:
                    campaign.emails_opened += 1
            
        elif event_type == "click":
            email_record.status = EmailStatus.CLICKED
            email_record.clicked_at = datetime.utcnow()
            email_record.click_count += 1
            
            # 更新活動統計
            if email_record.campaign_id:
                campaign = db.query(Campaign).filter(Campaign.id == email_record.campaign_id).first()
                if campaign:
                    campaign.emails_clicked += 1
            
        elif event_type == "bounce":
            email_record.status = EmailStatus.BOUNCED
            
            if email_record.campaign_id:
                campaign = db.query(Campaign).filter(Campaign.id == email_record.campaign_id).first()
                if campaign:
                    campaign.emails_bounced += 1
            
        elif event_type == "unsubscribe":
            email_record.status = EmailStatus.UNSUBSCRIBED
            
            if email_record.campaign_id:
                campaign = db.query(Campaign).filter(Campaign.id == email_record.campaign_id).first()
                if campaign:
                    campaign.unsubscribes += 1
        
        # 記錄活動
        activity_map = {
            "delivered": ActivityType.EMAIL_DELIVERED,
            "open": ActivityType.EMAIL_OPENED,
            "click": ActivityType.EMAIL_CLICKED,
            "bounce": ActivityType.EMAIL_BOUNCED,
            "unsubscribe": ActivityType.EMAIL_UNSUBSCRIBED,
        }
        
        if event_type in activity_map:
            log = ActivityLog(
                user_id=user_id,
                email_id=email_record.id,
                activity_type=activity_map[event_type],
                title=f"郵件{event_type}",
                description=f"郵件狀態更新: {event_type}",
                success=True,
            )
            db.add(log)
        
        db.commit()
        
        return {"success": True, "event": event_type}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {"error": str(e)}
        
    finally:
        db.close()


@celery_app.task
def warmup_email_accounts():
    """郵件預熱任務"""
    db = SessionLocal()
    
    try:
        # 獲取所有有 SendGrid 配置的用戶
        users = db.query(User).filter(
            User.sendgrid_api_key.isnot(None),
            User.is_active == True
        ).all()
        
        sender = SenderAgent(0, db)
        results = []
        
        for user in users:
            result = sender.warmup_account(user)
            results.append({
                "user_id": user.id,
                "result": result
            })
        
        return {"processed": len(users), "results": results}
        
    except Exception as e:
        logger.error(f"Error warming up email accounts: {str(e)}")
        return {"error": str(e)}
        
    finally:
        db.close()
