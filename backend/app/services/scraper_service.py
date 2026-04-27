"""
爬蟲服務
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.supplier import Supplier, SourcePlatform, VerificationStatus
from app.agents.scout_agent import ScoutAgent
from loguru import logger


class ScraperService:
    """爬蟲服務"""
    
    def __init__(self, user_id: int, db: Session):
        self.user_id = user_id
        self.db = db
        self.scout = ScoutAgent(user_id, db)
    
    def scrape_platform(
        self,
        platform: SourcePlatform,
        url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        爬取指定平台
        
        Args:
            platform: 平台名稱
            url: 可選的 URL
            
        Returns:
            爬取結果
        """
        try:
            if platform == SourcePlatform.ESOURCES:
                suppliers = self.scout.scrape_esources(url)
            elif platform == SourcePlatform.CREOATE:
                suppliers = self.scout.scrape_creoate(url)
            elif platform == SourcePlatform.THEWHOLESALER:
                suppliers = self.scout.scrape_thewholesaler(url)
            else:
                return {"error": f"Unknown platform: {platform}"}
            
            # 保存供應商
            saved = self._save_suppliers(suppliers, platform)
            
            return {
                "success": True,
                "platform": platform.value,
                "scraped": len(suppliers),
                "saved": saved
            }
            
        except Exception as e:
            logger.error(f"Error scraping platform {platform}: {str(e)}")
            return {"error": str(e)}
    
    def _save_suppliers(
        self,
        suppliers_data: List[Dict[str, Any]],
        platform: SourcePlatform
    ) -> int:
        """
        保存供應商到數據庫
        
        Args:
            suppliers_data: 供應商數據列表
            platform: 平台名稱
            
        Returns:
            保存的數量
        """
        saved_count = 0
        
        for data in suppliers_data:
            # 檢查是否已存在
            existing = None
            if data.get("email"):
                existing = self.db.query(Supplier).filter(
                    Supplier.owner_id == self.user_id,
                    Supplier.email == data.get("email")
                ).first()
            
            if existing:
                continue
            
            # 創建新供應商
            supplier = Supplier(
                owner_id=self.user_id,
                source_platform=platform,
                source_url=data.get("source_url"),
                source_page_title=data.get("source_page_title"),
                company_name=data.get("company_name", ""),
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
            
            self.db.add(supplier)
            saved_count += 1
        
        self.db.commit()
        return saved_count
    
    def verify_supplier(self, supplier_id: int) -> Dict[str, Any]:
        """
        驗證供應商
        
        Args:
            supplier_id: 供應商 ID
            
        Returns:
            驗證結果
        """
        supplier = self.db.query(Supplier).filter(
            Supplier.id == supplier_id,
            Supplier.owner_id == self.user_id
        ).first()
        
        if not supplier:
            return {"error": "Supplier not found"}
        
        result = self.scout.verify_supplier(supplier)
        
        supplier.verification_status = result["status"]
        supplier.verification_notes = result.get("notes")
        supplier.quality_score = result.get("quality_score", 0)
        supplier.verified_at = result.get("verified_at")
        
        self.db.commit()
        
        return result
    
    def batch_verify(
        self,
        supplier_ids: List[int] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        批量驗證供應商
        
        Args:
            supplier_ids: 指定供應商 ID 列表
            limit: 限制數量
            
        Returns:
            驗證結果
        """
        query = self.db.query(Supplier).filter(
            Supplier.owner_id == self.user_id,
            Supplier.verification_status == VerificationStatus.PENDING,
            Supplier.email.isnot(None),
            Supplier.is_blacklisted == False
        )
        
        if supplier_ids:
            query = query.filter(Supplier.id.in_(supplier_ids))
        
        suppliers = query.limit(limit).all()
        
        verified = 0
        invalid = 0
        pending = 0
        
        for supplier in suppliers:
            result = self.scout.verify_supplier(supplier)
            
            supplier.verification_status = result["status"]
            supplier.verification_notes = result.get("notes")
            supplier.quality_score = result.get("quality_score", 0)
            supplier.verified_at = result.get("verified_at")
            
            if result["status"] == VerificationStatus.VERIFIED:
                verified += 1
            elif result["status"] == VerificationStatus.INVALID:
                invalid += 1
            else:
                pending += 1
        
        self.db.commit()
        
        return {
            "total": len(suppliers),
            "verified": verified,
            "invalid": invalid,
            "pending": pending
        }
