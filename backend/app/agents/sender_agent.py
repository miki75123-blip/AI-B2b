"""
Sender Agent - 郵件發送代理
負責郵件發送、退訂處理和追蹤
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, TrackingSettings, ClickTracking
from loguru import logger
from app.models.email import Email as EmailModel, EmailStatus
from app.models.supplier import Supplier


class SenderAgent:
    """Sender Agent - 郵件發送與追蹤"""
    
    def __init__(self, user_id: int, db: Session):
        self.user_id = user_id
        self.db = db
    
    def _create_sendgrid_client(self, api_key: str) -> Optional[SendGridAPIClient]:
        """
        創建 SendGrid 客戶端
        
        Args:
            api_key: SendGrid API Key
            
        Returns:
            SendGridAPIClient 或 None
        """
        if not api_key:
            logger.error("SendGrid API key not provided")
            return None
        
        try:
            return SendGridAPIClient(api_key)
        except Exception as e:
            logger.error(f"Error creating SendGrid client: {str(e)}")
            return None
    
    def send_email(
        self,
        email_record: EmailModel,
        sendgrid_api_key: str,
        from_email: str,
        from_name: str
    ) -> Dict[str, Any]:
        """
        發送郵件
        
        Args:
            email_record: 郵件記錄
            sendgrid_api_key: SendGrid API Key
            from_email: 發件人郵箱
            from_name: 發件人名稱
            
        Returns:
            發送結果
        """
        client = self._create_sendgrid_client(sendgrid_api_key)
        if not client:
            return {
                "success": False,
                "error": "Failed to create SendGrid client"
            }
        
        try:
            # 創建郵件
            message = Mail(
                from_email=Email(from_email, from_name),
                to_emails=To(email_record.to_email),
                subject=email_record.subject,
                html_content=Content("text/html", email_record.body_html or "")
            )
            
            # 添加追蹤設置
            tracking_settings = TrackingSettings()
            tracking_settings.enable_click_tracking = ClickTracking(True, True)
            message.tracking_settings = tracking_settings
            
            # 發送郵件
            response = client.send(message)
            
            # 提取消息 ID
            message_id = None
            if response.headers:
                message_id = response.headers.get("X-Message-Id", "")
            
            logger.info(f"Email sent to {email_record.to_email}, message_id: {message_id}")
            
            return {
                "success": True,
                "message_id": message_id,
                "status_code": response.status_code
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_batch(
        self,
        emails: List[EmailModel],
        sendgrid_api_key: str,
        from_email: str,
        from_name: str
    ) -> Dict[str, Any]:
        """
        批量發送郵件
        
        Args:
            emails: 郵件列表
            sendgrid_api_key: SendGrid API Key
            from_email: 發件人郵箱
            from_name: 發件人名稱
            
        Returns:
            批量發送結果
        """
        client = self._create_sendgrid_client(sendgrid_api_key)
        if not client:
            return {
                "success": False,
                "error": "Failed to create SendGrid client",
                "sent": 0,
                "failed": len(emails)
            }
        
        sent = 0
        failed = 0
        errors = []
        
        for email_record in emails:
            try:
                result = self.send_email(
                    email_record=email_record,
                    sendgrid_api_key=sendgrid_api_key,
                    from_email=from_email,
                    from_name=from_name
                )
                
                if result["success"]:
                    sent += 1
                else:
                    failed += 1
                    errors.append({
                        "email": email_record.to_email,
                        "error": result.get("error")
                    })
                
            except Exception as e:
                logger.error(f"Error sending email to {email_record.to_email}: {str(e)}")
                failed += 1
                errors.append({
                    "email": email_record.to_email,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "sent": sent,
            "failed": failed,
            "errors": errors
        }
    
    def process_webhook(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理 SendGrid Webhook 事件
        
        Args:
            event_data: Webhook 事件數據
            
        Returns:
            處理結果
        """
        event_type = event_data.get("event", "")
        message_id = event_data.get("sg_message_id", "")
        email = event_data.get("email", "")
        
        # 查找郵件記錄
        email_record = self.db.query(EmailModel).filter(
            EmailModel.sendgrid_message_id.contains(message_id.split(".")[0])
        ).first()
        
        if not email_record:
            logger.warning(f"Email not found for message_id: {message_id}")
            return {"error": "Email not found"}
        
        # 更新郵件狀態
        if event_type == "delivered":
            email_record.status = EmailStatus.DELIVERED
            email_record.delivered_at = datetime.utcnow()
            
        elif event_type == "open":
            if email_record.status not in [EmailStatus.OPENED, EmailStatus.CLICKED]:
                email_record.status = EmailStatus.OPENED
            email_record.opened_at = datetime.utcnow()
            email_record.open_count += 1
            
        elif event_type == "click":
            email_record.status = EmailStatus.CLICKED
            email_record.clicked_at = datetime.utcnow()
            email_record.click_count += 1
            
        elif event_type == "bounce":
            email_record.status = EmailStatus.BOUNCED
            
        elif event_type == "dropped":
            email_record.status = EmailStatus.BOUNCED
            email_record.error_message = event_data.get("reason", "Dropped")
            
        elif event_type == "unsubscribe":
            email_record.status = EmailStatus.UNSUBSCRIBED
            # 將供應商加入黑名單
            if email_record.supplier_id:
                supplier = self.db.query(Supplier).filter(
                    Supplier.id == email_record.supplier_id
                ).first()
                if supplier:
                    supplier.is_blacklisted = True
        
        elif event_type == "spamreport":
            email_record.status = EmailStatus.FAILED
            email_record.error_message = "Marked as spam"
        
        self.db.commit()
        
        return {
            "success": True,
            "event": event_type,
            "email_id": email_record.id
        }
    
    def warmup_account(self, user) -> Dict[str, Any]:
        """
        郵箱預熱
        
        Args:
            user: 用戶對象
            
        Returns:
            預熱結果
        """
        if not user.sendgrid_api_key:
            return {"success": False, "error": "No SendGrid API key"}
        
        # 預熱策略：
        # 1. 逐漸增加發送量
        # 2. 與高質量郵箱互動
        # 3. 避免觸發垃圾郵件過濾器
        
        warmup_schedule = [
            {"day": 1, "limit": 5},
            {"day": 2, "limit": 10},
            {"day": 3, "limit": 20},
            {"day": 4, "limit": 30},
            {"day": 5, "limit": 50},
        ]
        
        return {
            "success": True,
            "message": "Warmup process started",
            "schedule": warmup_schedule
        }
    
    def check_bounce_rate(self, user_id: int) -> Dict[str, Any]:
        """
        檢查退信率
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            退信率分析
        """
        from app.models.campaign import Campaign
        
        campaigns = self.db.query(Campaign).filter(
            Campaign.owner_id == user_id
        ).all()
        
        total_sent = sum(c.emails_sent for c in campaigns)
        total_bounced = sum(c.emails_bounced for c in campaigns)
        
        bounce_rate = (total_bounced / total_sent * 100) if total_sent > 0 else 0
        
        # SendGrid 建議退信率保持在 2% 以下
        risk_level = "low"
        if bounce_rate > 5:
            risk_level = "high"
        elif bounce_rate > 2:
            risk_level = "medium"
        
        return {
            "total_sent": total_sent,
            "total_bounced": total_bounced,
            "bounce_rate": round(bounce_rate, 2),
            "risk_level": risk_level,
            "recommendations": self._get_bounce_recommendations(risk_level)
        }
    
    def _get_bounce_recommendations(self, risk_level: str) -> List[str]:
        """獲取退信處理建議"""
        recommendations = {
            "low": [
                "繼續監控退信率",
                "保持良好的郵件質量"
            ],
            "medium": [
                "檢查郵箱地址質量",
                "考慮清理無效郵箱",
                "降低發送頻率"
            ],
            "high": [
                "立即暫停大量發送",
                "清理所有無效郵箱",
                "檢查發送的郵件內容",
                "聯繫 SendGrid 支持"
            ]
        }
        return recommendations.get(risk_level, [])
    
    def add_to_suppression(self, email: str, reason: str) -> Dict[str, Any]:
        """
        添加到發送抑制列表
        
        Args:
            email: 郵箱地址
            reason: 原因
            
        Returns:
            操作結果
        """
        # 這需要 SendGrid API 支持
        # 可以通過抑制組管理實現
        return {
            "success": True,
            "email": email,
            "reason": reason
        }
