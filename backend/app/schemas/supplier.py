"""
供應商 Pydantic Schema
"""
from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SourcePlatform(str, Enum):
    """數據來源平台"""
    ESOURCES = "esources"
    CREOATE = "creoate"
    THEWHOLESALER = "thewholesaler"
    MANUAL = "manual"
    IMPORT = "import"


class VerificationStatus(str, Enum):
    """驗證狀態"""
    PENDING = "pending"
    VERIFIED = "verified"
    INVALID = "invalid"
    DUPLICATE = "duplicate"


class SupplierBase(BaseModel):
    """供應商基礎 Schema"""
    company_name: str = Field(..., min_length=1, max_length=255)
    website: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    business_type: Optional[str] = None
    product_categories: Optional[List[str]] = None
    min_order_quantity: Optional[str] = None
    price_range: Optional[str] = None
    certifications: Optional[List[str]] = None
    description: Optional[str] = None
    about_us: Optional[str] = None
    tags: Optional[List[str]] = None


class SupplierCreate(SupplierBase):
    """供應商創建 Schema"""
    source_platform: SourcePlatform = SourcePlatform.MANUAL
    source_url: Optional[str] = None
    raw_data: Optional[dict] = None


class SupplierUpdate(BaseModel):
    """供應商更新 Schema"""
    company_name: Optional[str] = None
    website: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    business_type: Optional[str] = None
    product_categories: Optional[List[str]] = None
    min_order_quantity: Optional[str] = None
    price_range: Optional[str] = None
    certifications: Optional[List[str]] = None
    description: Optional[str] = None
    about_us: Optional[str] = None
    tags: Optional[List[str]] = None
    verification_status: Optional[VerificationStatus] = None
    verification_notes: Optional[str] = None
    is_blacklisted: Optional[bool] = None


class SupplierResponse(SupplierBase):
    """供應商響應 Schema"""
    id: int
    owner_id: int
    source_platform: SourcePlatform
    source_url: Optional[str]
    verification_status: VerificationStatus
    quality_score: float
    is_contacted: bool
    is_customer: bool
    is_blacklisted: bool
    created_at: datetime
    updated_at: datetime
    last_contacted_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SupplierList(BaseModel):
    """供應商列表響應"""
    items: List[SupplierResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SupplierImport(BaseModel):
    """批量導入 Schema"""
    suppliers: List[SupplierCreate]
