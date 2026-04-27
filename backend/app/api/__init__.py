"""
API 路由
"""
from fastapi import APIRouter
from app.api import auth, users, suppliers, campaigns, emails, activities, dashboard

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["認證"])
api_router.include_router(users.router, prefix="/users", tags=["用戶"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["供應商"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["活動"])
api_router.include_router(emails.router, prefix="/emails", tags=["郵件"])
api_router.include_router(activities.router, prefix="/activities", tags=["活動日誌"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["儀表板"])
