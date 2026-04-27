"""
優化器任務
"""
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.campaign import Campaign, CampaignStatus
from app.models.email import Email, EmailTemplate, EmailStatus
from app.models.supplier import Supplier
from app.models.learning_pattern import LearningPattern
from app.agents.optimizer_agent import OptimizerAgent
from loguru import logger
from datetime import datetime, timedelta


@celery_app.task
def run_daily_optimization():
    """每日優化任務"""
    db = SessionLocal()
    
    try:
        # 獲取所有活躍用戶
        users = db.query(User).filter(User.is_active == True).all()
        
        results = []
        
        for user in users:
            optimizer = OptimizerAgent(user.id, db)
            
            # 分析過去一天的數據
            analysis = optimizer.analyze_performance()
            
            # 生成優化建議
            suggestions = optimizer.generate_suggestions(analysis)
            
            # 應用優化
            applied = optimizer.apply_optimizations(suggestions)
            
            results.append({
                "user_id": user.id,
                "analysis": analysis,
                "suggestions": suggestions,
                "applied": applied
            })
            
            logger.info(f"Optimization completed for user {user.id}")
        
        return {
            "processed_users": len(users),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in daily optimization: {str(e)}")
        return {"error": str(e)}
        
    finally:
        db.close()


@celery_app.task
def learn_from_campaign_task(campaign_id: int):
    """
    從活動中學習任務
    
    Args:
        campaign_id: 活動 ID
    """
    db = SessionLocal()
    
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return {"error": "Campaign not found"}
        
        optimizer = OptimizerAgent(campaign.owner_id, db)
        
        # 分析活動數據
        patterns = optimizer.learn_from_campaign(campaign)
        
        # 保存學習到的模式
        for pattern_data in patterns:
            existing = db.query(LearningPattern).filter(
                LearningPattern.owner_id == campaign.owner_id,
                LearningPattern.pattern_type == pattern_data["pattern_type"],
                LearningPattern.pattern_name == pattern_data["pattern_name"]
            ).first()
            
            if existing:
                # 更新現有模式
                existing.strategy = pattern_data["strategy"]
                existing.success_rate = pattern_data.get("success_rate", 0)
                existing.sample_size = pattern_data.get("sample_size", 0)
                existing.confidence = pattern_data.get("confidence", 0)
                existing.updated_at = datetime.utcnow()
            else:
                # 創建新模式
                pattern = LearningPattern(
                    owner_id=campaign.owner_id,
                    **pattern_data
                )
                db.add(pattern)
        
        db.commit()
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "patterns_learned": len(patterns)
        }
        
    except Exception as e:
        logger.error(f"Error learning from campaign {campaign_id}: {str(e)}")
        return {"error": str(e)}
        
    finally:
        db.close()


@celery_app.task
def generate_optimization_report_task(user_id: int):
    """
    生成優化報告任務
    
    Args:
        user_id: 用戶 ID
    """
    db = SessionLocal()
    
    try:
        optimizer = OptimizerAgent(user_id, db)
        
        # 生成報告
        report = optimizer.generate_report()
        
        return {
            "success": True,
            "user_id": user_id,
            "report": report
        }
        
    except Exception as e:
        logger.error(f"Error generating optimization report for user {user_id}: {str(e)}")
        return {"error": str(e)}
        
    finally:
        db.close()


@celery_app.task
def apply_best_practices_task(user_id: int):
    """應用最佳實踐任務"""
    db = SessionLocal()
    
    try:
        optimizer = OptimizerAgent(user_id, db)
        
        # 獲取所有高置信度的模式
        patterns = db.query(LearningPattern).filter(
            LearningPattern.owner_id == user_id,
            LearningPattern.is_active == True,
            LearningPattern.confidence >= 0.7
        ).all()
        
        applied_count = 0
        
        for pattern in patterns:
            # 應用策略
            success = optimizer.apply_pattern(pattern)
            
            if success:
                pattern.is_applied = True
                pattern.times_applied += 1
                applied_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "user_id": user_id,
            "patterns_applied": applied_count
        }
        
    except Exception as e:
        logger.error(f"Error applying best practices for user {user_id}: {str(e)}")
        return {"error": str(e)}
        
    finally:
        db.close()
