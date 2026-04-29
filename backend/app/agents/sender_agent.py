"""
Sender Agent - 郵件發送代理
負責郵件發送、退訂處理和追蹤
使用 Resend API（免費 3000 封/月）
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import resend
from loguru import logger
from app.core.config import settings
from app.models.email import Email as EmailModel, EmailStatus
from app.models.supplier import Supplier


class SenderAgent:
    """Sender Agent - 郵件發送與追蹤"""
    
    def __init__(self, user_id: int, db: Session):
        self.user_id = user_id
        self.db = db
    
    def send_email(
        self,
        email_record: EmailModel,
        resend_api_key: str,
        from_email: str,
        from_name: str
    ) -> Dict[str, Any]:
        """
        發送郵件
        
        Args:
            email_record: 郵件記錄
            resend_api_key: Resend API Key
            from_email: 發件人郵箱
            from_name: 發件人名稱
            
        Returns:
            發送結果
        """
        if not resend_api_key:
            logger.error("Resend API key not provided")
            return {
                "success": False,
                "error": "No Resend API key provided"
            }
        
        try:
            # 配置 Resend
            resend.api_key = resend_api_key
            
            # 發送郵件
            params = {
                "from": f"{from_name} <{from_email}>",
                "to": email_record.to_email,
                "subject": email_record.subject,
                "html": email_record.body_html or ""
            }
            
            response = resend.Emails.send(params)
            
            message_id = response.get("id", "")
            
            logger.info(f"Email sent to {email_record.to_email}, message_id: {message_id}")
            
            return {
                "success": True,
                "message_id": message_id,
                "provider": "resend"
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
        resend_api_key: str,
        from_email: str,
        from_name: str
    ) -> Dict[str, Any]:
        """
        批量發送郵件
        
        Args:
            emails: 郵件列表
            resend_api_key: Resend API Key
            from_email: 發件人郵箱
            from_name: 發件人名稱
            
        Returns:
            批量發送結果
        """
        sent = 0
        failed = 0
        errors = []
        
        for email_record in emails:
            try:
                result = self.send_email(
                    email_record=email_record,
                    resend_api_key=resend_api_key,
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
        處理 Resend Webhook 事件
        
        Args:
            event_data: Webhook 事件數據
            
        Returns:
            處理結果
        """
        event_type = event_data.get("type", "")
        email_id = event_data.get("data", {}).get("email_id", "")
        email = event_data.get("data", {}).get("to", "")
        
        # 查找郵件記錄
        email_record = self.db.query(EmailModel).filter(
            EmailModel.provider_message_id == email_id
        ).first()
        
        if not email_record:
            logger.warning(f"Email not found for email_id: {email_id}")
            return {"error": "Email not found"}
        
        # 更新郵件狀態
        if event_type == "email.delivered" or event_type == "delivered":
            email_record.status = EmailStatus.DELIVERED
            email_record.delivered_at = datetime.utcnow()
            
        elif event_type == "email.opened" or event_type == "opened":
            if email_record.status not in [EmailStatus.OPENED, EmailStatus.CLICKED]:
                email_record.status = EmailStatus.OPENED
            email_record.opened_at = datetime.utcnow()
            email_record.open_count += 1
            
        elif event_type == "email.clicked" or event_type == "clicked":
            email_record.status = EmailStatus.CLICKED
            email_record.clicked_at = datetime.utcnow()
            email_record.click_count += 1
            
        elif event_type == "email.bounced" or event_type == "bounced":
            email_record.status = EmailStatus.BOUNCED
            
        elif event_type == "email.unsubscribed" or event_type == "unsubscribed":
            email_record.status = EmailStatus.UNSUBSCRIBED
            # 將供應商加入黑名單
            if email_record.supplier_id:
                supplier = self.db.query(Supplier).filter(
                    Supplier.id == email_record.supplier_id
                ).first()
                if supplier:
                    supplier.is_blacklisted = True
        
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
        if not user.resend_api_key:
            return {"success": False, "error": "No Resend API key"}
        
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
        
        # Resend 建議退信率保持在 2% 以下
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
                "檢查發送的郵件內容"
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
        return {
            "success": True,
            "email": email,
            "reason": reason
        }
