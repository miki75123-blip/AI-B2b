"""
數據庫模型
"""
from app.models.user import User
from app.models.supplier import Supplier
from app.models.campaign import Campaign
from app.models.email import Email, EmailTemplate
from app.models.activity_log import ActivityLog
from app.models.learning_pattern import LearningPattern

__all__ = [
    "User",
    "Supplier",
    "Campaign",
    "Email",
    "EmailTemplate",
    "ActivityLog",
    "LearningPattern",
]
