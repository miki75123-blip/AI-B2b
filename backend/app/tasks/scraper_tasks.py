"""
爬蟲任務
"""
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.supplier import Supplier, SourcePlatform, VerificationStatus
from app.models.user import User
from app.models.activity_log import ActivityLog, ActivityType
from app.agents.scout_agent import ScoutAgent
from loguru import logger
import traceback


@celery_app.task(bind=True, max_retries=3)
def scrape_suppliers_task(self, user_id: int, platform: str, url: str = None):
    """
    爬取供應商任務
    
    Args:
        user_id: 用戶 ID
        platform: 平台名稱
        url: 可選的特定 URL
    """
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {"error": "User not found"}
        
        # 創建 Scout Agent
        scout = ScoutAgent(user_id, db)
        
        # 根據平台執行爬取
        if platform == SourcePlatform.ESOURCES.value:
            suppliers_data = scout.scrape_esources(url)
        elif platform == SourcePlatform.CREOATE.value:
            suppliers_data = scout.scrape_creoate(url)
        elif platform == SourcePlatform.THEWHOLESALER.value:
            suppliers_data = scout.scrape_thewholesaler(url)
        else:
            return {"error": f"Unknown platform: {platform}"}
        
        # 保存供應商
        saved_count = 0
        for data in suppliers_data:
            # 檢查是否已存在
            existing = db.query(Supplier).filter(
                Supplier.owner_id == user_id,
                Supplier.email == data.get("email")
            ).first()
            
            if not existing:
                supplier = Supplier(
                    owner_id=user_id,
                    source_platform=SourcePlatform(platform),
                    source_url=data.get("source_url"),
                    source_page_title=data.get("source_page_title"),
                    company_name=data.get("company_name"),
                    website=data.get("website"),
                    email=data.get("email"),
                    phone=data.get("phone"),
                    address=data.get("address"),
                    country=data.get("country"),
                    city=data.get("city"),
                    business_type=data.get("business_type"),
                    product_categories=data.get("product_categories"),
                    description=data.get("description"),
                    raw_data=data.get("raw_data"),
                    verification_status=VerificationStatus.PENDING,
                )
                db.add(supplier)
                saved_count += 1
        
        db.commit()
        
        # 記錄活動
        log = ActivityLog(
            user_id=user_id,
            activity_type=ActivityType.SUPPLIER_SCRAPED,
            title="爬取供應商完成",
            description=f"從 {platform} 爬取並保存了 {saved_count} 個供應商",
            metadata={"platform": platform, "saved": saved_count, "total": len(suppliers_data)},
            success=True,
        )
        db.add(log)
        db.commit()
        
        logger.info(f"Scraped {saved_count} suppliers from {platform}")
        
        return {
            "success": True,
            "platform": platform,
            "saved": saved_count,
            "total": len(suppliers_data)
        }
        
    except Exception as e:
        logger.error(f"Error scraping suppliers: {str(e)}")
        logger.error(traceback.format_exc())
        
        # 記錄錯誤
        log = ActivityLog(
            user_id=user_id,
            activity_type=ActivityType.SYSTEM_ERROR,
            title="爬取供應商失敗",
            description=f"爬取任務失敗: {str(e)}",
            metadata={"platform": platform, "error": str(e)},
            success=False,
            error_message=traceback.format_exc(),
        )
        db.add(log)
        db.commit()
        
        # 重試
        raise self.retry(exc=e, countdown=60)
        
    finally:
        db.close()


@celery_app.task
def verify_supplier_task(supplier_id: int):
    """驗證供應商任務"""
    db = SessionLocal()
    
    try:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return {"error": "Supplier not found"}
        
        # 創建 Scout Agent
        scout = ScoutAgent(supplier.owner_id, db)
        
        # 驗證供應商
        result = scout.verify_supplier(supplier)
        
        # 更新狀態
        supplier.verification_status = result["status"]
        supplier.verification_notes = result.get("notes")
        supplier.quality_score = result.get("quality_score", 0)
        supplier.verified_at = result.get("verified_at")
        
        db.commit()
        
        return result
        
    except Exception as e:
        logger.error(f"Error verifying supplier {supplier_id}: {str(e)}")
        return {"error": str(e)}
        
    finally:
        db.close()


@celery_app.task
def batch_verify_suppliers_task(user_id: int, limit: int = 100):
    """批量驗證供應商任務"""
    db = SessionLocal()
    
    try:
        # 獲取待驗證的供應商
        suppliers = db.query(Supplier).filter(
            Supplier.owner_id == user_id,
            Supplier.verification_status == VerificationStatus.PENDING,
            Supplier.email.isnot(None),
            Supplier.is_blacklisted == False
        ).limit(limit).all()
        
        scout = ScoutAgent(user_id, db)
        results = []
        
        for supplier in suppliers:
            result = scout.verify_supplier(supplier)
            supplier.verification_status = result["status"]
            supplier.verification_notes = result.get("notes")
            supplier.quality_score = result.get("quality_score", 0)
            supplier.verified_at = result.get("verified_at")
            results.append(result)
        
        db.commit()
        
        return {
            "total": len(suppliers),
            "verified": sum(1 for r in results if r["status"] == VerificationStatus.VERIFIED),
            "invalid": sum(1 for r in results if r["status"] == VerificationStatus.INVALID),
        }
        
    except Exception as e:
        logger.error(f"Error batch verifying suppliers: {str(e)}")
        return {"error": str(e)}
        
    finally:
        db.close()
