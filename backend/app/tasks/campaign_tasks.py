"""
營銷活動任務
"""
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.campaign import Campaign, CampaignStatus
from app.models.supplier import Supplier
from app.tasks.email_tasks import batch_send_emails_task
from loguru import logger


@celery_app.task
def run_campaign_task(campaign_id: int):
    """
    運行營銷活動任務
    
    Args:
        campaign_id: 活動 ID
    """
    db = SessionLocal()
    
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found")
            return {"error": "Campaign not found"}
        
        if campaign.status != CampaignStatus.RUNNING:
            logger.warning(f"Campaign {campaign_id} is not running")
            return {"error": "Campaign is not running"}
        
        # 觸發批量發送任務
        batch_send_emails_task.delay(campaign_id)
        
        logger.info(f"Campaign {campaign_id} started")
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "message": "Campaign processing started"
        }
        
    except Exception as e:
        logger.error(f"Error running campaign {campaign_id}: {str(e)}")
        return {"error": str(e)}
        
    finally:
        db.close()


@celery_app.task
def pause_campaign_task(campaign_id: int):
    """
    暫停營銷活動任務
    
    Args:
        campaign_id: 活動 ID
    """
    db = SessionLocal()
    
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        
        if not campaign:
            return {"error": "Campaign not found"}
        
        # 活動狀態已在 API 中更新
        # 這裡可以添加其他清理邏輯
        
        logger.info(f"Campaign {campaign_id} paused")
        
        return {
            "success": True,
            "campaign_id": campaign_id
        }
        
    except Exception as e:
        logger.error(f"Error pausing campaign {campaign_id}: {str(e)}")
        return {"error": str(e)}
        
    finally:
        db.close()


@celery_app.task
def check_and_process_campaigns():
    """檢查並處理運行中的活動"""
    db = SessionLocal()
    
    try:
        # 獲取所有運行中的活動
        campaigns = db.query(Campaign).filter(
            Campaign.status == CampaignStatus.RUNNING
        ).all()
        
        results = []
        
        for campaign in campaigns:
            # 檢查是否可以繼續發送
            remaining = campaign.total_send_limit - campaign.emails_sent
            
            if remaining > 0:
                # 觸發批量發送
                batch_send_emails_task.delay(campaign.id)
                results.append({
                    "campaign_id": campaign.id,
                    "action": "triggered"
                })
            else:
                # 完成活動
                campaign.status = CampaignStatus.COMPLETED
                from datetime import datetime
                campaign.completed_at = datetime.utcnow()
                results.append({
                    "campaign_id": campaign.id,
                    "action": "completed"
                })
        
        db.commit()
        
        return {
            "processed": len(campaigns),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error checking campaigns: {str(e)}")
        return {"error": str(e)}
        
    finally:
        db.close()


@celery_app.task
def schedule_campaign_task(campaign_id: int, scheduled_time: str):
    """
    排程活動任務
    
    Args:
        campaign_id: 活動 ID
        scheduled_time: 計劃運行時間 (ISO 格式)
    """
    from datetime import datetime
    
    # 計算延遲秒數
    scheduled_dt = datetime.fromisoformat(scheduled_time)
    delay_seconds = (scheduled_dt - datetime.utcnow()).total_seconds()
    
    if delay_seconds > 0:
        # 延遲執行
        run_campaign_task.apply_async(
            args=[campaign_id],
            countdown=delay_seconds
        )
        return {
            "success": True,
            "scheduled_for": scheduled_time,
            "delay_seconds": delay_seconds
        }
    else:
        # 立即執行
        run_campaign_task.delay(campaign_id)
        return {
            "success": True,
            "message": "Scheduled time has passed, running now"
        }
