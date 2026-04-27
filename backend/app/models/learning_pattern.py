"""
學習模式模型 - 用於 Optimizer Agent 存儲學習到的模式
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON
from datetime import datetime
from app.core.database import Base


class LearningPattern(Base):
    """學習模式模型"""
    
    __tablename__ = "learning_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 模式類型
    pattern_type = Column(String(100), nullable=False, index=True)
    # 例如: subject_optimization, timing_optimization, content_optimization
    
    # 模式描述
    pattern_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # 觸發條件
    trigger_conditions = Column(JSON)
    # 例如: {"country": "UK", "business_type": "wholesaler"}
    
    # 學習到的策略
    strategy = Column(JSON, nullable=False)
    # 例如: {"subject_prefix": "Special Offer", "send_hour": 9}
    
    # 效果指標
    success_rate = Column(Float, default=0.0)
    sample_size = Column(Integer, default=0)
    
    # 置信度
    confidence = Column(Float, default=0.0)  # 0-1
    min_confidence_threshold = Column(Float, default=0.7)
    
    # 狀態
    is_active = Column(Boolean, default=True)
    is_applied = Column(Boolean, default=False)
    times_applied = Column(Integer, default=0)
    
    # 有效期
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<LearningPattern {self.pattern_type} - {self.pattern_name}>"
