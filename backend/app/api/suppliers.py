"""
供應商 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from app.core.database import get_db
from app.models.user import User
from app.models.supplier import Supplier, SourcePlatform, VerificationStatus
from app.models.activity_log import ActivityLog, ActivityType
from app.schemas.supplier import (
    SupplierCreate, SupplierUpdate, SupplierResponse, SupplierList, SupplierImport
)
from app.api.auth import get_current_user
from app.tasks.scraper_tasks import scrape_suppliers_task
import csv
import io

router = APIRouter()


def supplier_to_response(supplier: Supplier) -> SupplierResponse:
    """將 Supplier 模型轉換為響應 Schema"""
    return SupplierResponse(
        id=supplier.id,
        owner_id=supplier.owner_id,
        company_name=supplier.company_name,
        website=supplier.website,
        email=supplier.email,
        phone=supplier.phone,
        address=supplier.address,
        country=supplier.country,
        city=supplier.city,
        business_type=supplier.business_type,
        product_categories=supplier.product_categories,
        min_order_quantity=supplier.min_order_quantity,
        price_range=supplier.price_range,
        certifications=supplier.certifications,
        description=supplier.description,
        about_us=supplier.about_us,
        tags=supplier.tags,
        source_platform=supplier.source_platform,
        source_url=supplier.source_url,
        verification_status=supplier.verification_status,
        quality_score=supplier.quality_score,
        is_contacted=supplier.is_contacted,
        is_customer=supplier.is_customer,
        is_blacklisted=supplier.is_blacklisted,
        created_at=supplier.created_at,
        updated_at=supplier.updated_at,
        last_contacted_at=supplier.last_contacted_at,
    )


@router.get("/", response_model=SupplierList)
def list_suppliers(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    country: Optional[str] = None,
    business_type: Optional[str] = None,
    verification_status: Optional[VerificationStatus] = None,
    is_contacted: Optional[bool] = None,
    is_blacklisted: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """列出供應商"""
    query = db.query(Supplier).filter(Supplier.owner_id == current_user.id)
    
    # 搜索過濾
    if search:
        search_filter = or_(
            Supplier.company_name.ilike(f"%{search}%"),
            Supplier.email.ilike(f"%{search}%"),
            Supplier.description.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)
    
    # 其他過濾
    if country:
        query = query.filter(Supplier.country == country)
    if business_type:
        query = query.filter(Supplier.business_type == business_type)
    if verification_status:
        query = query.filter(Supplier.verification_status == verification_status)
    if is_contacted is not None:
        query = query.filter(Supplier.is_contacted == is_contacted)
    if is_blacklisted is not None:
        query = query.filter(Supplier.is_blacklisted == is_blacklisted)
    
    # 總數
    total = query.count()
    
    # 分頁
    offset = (page - 1) * page_size
    suppliers = query.order_by(Supplier.created_at.desc()).offset(offset).limit(page_size).all()
    
    return SupplierList(
        items=[supplier_to_response(s) for s in suppliers],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total > 0 else 0
    )


@router.post("/", response_model=SupplierResponse)
def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """創建供應商"""
    supplier = Supplier(
        owner_id=current_user.id,
        **supplier_data.model_dump()
    )
    
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    
    # 記錄活動
    log = ActivityLog(
        user_id=current_user.id,
        supplier_id=supplier.id,
        activity_type=ActivityType.SUPPLIER_CREATED,
        title="創建供應商",
        description=f"創建了新供應商: {supplier.company_name}",
        success=True,
    )
    db.add(log)
    db.commit()
    
    return supplier_to_response(supplier)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """獲取供應商詳情"""
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.owner_id == current_user.id
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供應商不存在"
        )
    
    return supplier_to_response(supplier)


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新供應商"""
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.owner_id == current_user.id
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供應商不存在"
        )
    
    update_data = supplier_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)
    
    db.commit()
    db.refresh(supplier)
    
    # 記錄活動
    log = ActivityLog(
        user_id=current_user.id,
        supplier_id=supplier.id,
        activity_type=ActivityType.SUPPLIER_UPDATED,
        title="更新供應商",
        description=f"更新了供應商: {supplier.company_name}",
        success=True,
    )
    db.add(log)
    db.commit()
    
    return supplier_to_response(supplier)


@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """刪除供應商"""
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.owner_id == current_user.id
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供應商不存在"
        )
    
    db.delete(supplier)
    db.commit()
    
    return {"message": "供應商已刪除"}


@router.post("/import")
def import_suppliers(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量導入供應商"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持 CSV 文件"
        )
    
    content = file.file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(content))
    
    imported_count = 0
    duplicate_count = 0
    suppliers_data = []
    
    for row in reader:
        # 檢查是否已存在
        email = row.get('email', '').strip()
        if email:
            existing = db.query(Supplier).filter(
                Supplier.owner_id == current_user.id,
                Supplier.email == email
            ).first()
            if existing:
                duplicate_count += 1
                continue
        
        supplier = Supplier(
            owner_id=current_user.id,
            company_name=row.get('company_name', '').strip(),
            website=row.get('website', '').strip() or None,
            email=email or None,
            phone=row.get('phone', '').strip() or None,
            address=row.get('address', '').strip() or None,
            country=row.get('country', '').strip() or None,
            city=row.get('city', '').strip() or None,
            business_type=row.get('business_type', '').strip() or None,
            description=row.get('description', '').strip() or None,
            source_platform=SourcePlatform.IMPORT,
        )
        suppliers_data.append(supplier)
        imported_count += 1
    
    db.bulk_save_objects(suppliers_data)
    db.commit()
    
    # 記錄活動
    log = ActivityLog(
        user_id=current_user.id,
        activity_type=ActivityType.SUPPLIER_IMPORTED,
        title="批量導入供應商",
        description=f"導入了 {imported_count} 個供應商，跳過 {duplicate_count} 個重複",
        metadata={"imported": imported_count, "duplicates": duplicate_count},
        success=True,
    )
    db.add(log)
    db.commit()
    
    return {
        "message": f"成功導入 {imported_count} 個供應商",
        "imported": imported_count,
        "duplicates": duplicate_count
    }


@router.post("/scrape")
def start_scraping(
    platform: SourcePlatform,
    url: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """啟動爬蟲任務"""
    # 記錄活動
    log = ActivityLog(
        user_id=current_user.id,
        activity_type=ActivityType.SUPPLIER_SCRAPED,
        title="啟動爬蟲",
        description=f"開始從 {platform.value} 爬取供應商",
        metadata={"platform": platform.value, "url": url},
        success=True,
    )
    db.add(log)
    db.commit()
    
    # 觸發 Celery 任務
    task = scrape_suppliers_task.delay(current_user.id, platform.value, url)
    
    return {
        "message": "爬蟲任務已啟動",
        "task_id": task.id,
        "platform": platform.value
    }


@router.get("/{supplier_id}/blacklist", response_model=SupplierResponse)
def toggle_blacklist(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """切換黑名單狀態"""
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.owner_id == current_user.id
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供應商不存在"
        )
    
    supplier.is_blacklisted = not supplier.is_blacklisted
    db.commit()
    db.refresh(supplier)
    
    # 記錄活動
    log = ActivityLog(
        user_id=current_user.id,
        supplier_id=supplier.id,
        activity_type=ActivityType.SUPPLIER_BLACKLISTED,
        title="切換黑名單",
        description=f"供應商 {'已加入' if supplier.is_blacklisted else '已移除'}黑名單",
        success=True,
    )
    db.add(log)
    db.commit()
    
    return supplier_to_response(supplier)
