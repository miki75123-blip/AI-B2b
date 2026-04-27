"""
Optimizer Agent - 優化代理
負責持續學習和優化營銷策略
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from loguru import logger
from app.models.campaign import Campaign, CampaignStatus
from app.models.email import Email, EmailTemplate, EmailStatus
from app.models.supplier import Supplier
from app.models.learning_pattern import LearningPattern


class OptimizerAgent:
    """Optimizer Agent - 自我優化與策略學習"""
    
    def __init__(self, user_id: int, db: Session):
        self.user_id = user_id
        self.db = db
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        分析過去一段時間的表現
        
        Returns:
            性能分析結果
        """
        # 分析過去 7 天的數據
        start_date = datetime.utcnow() - timedelta(days=7)
        
        emails = self.db.query(Email).join(Email.supplier).filter(
            Email.supplier.has(owner_id=self.user_id),
            Email.sent_at >= start_date
        ).all()
        
        total_sent = len(emails)
        if total_sent == 0:
            return {
                "period": "7 days",
                "total_sent": 0,
                "message": "No emails sent in the past 7 days"
            }
        
        total_opened = sum(1 for e in emails if e.status in [EmailStatus.OPENED, EmailStatus.CLICKED])
        total_clicked = sum(1 for e in emails if e.status == EmailStatus.CLICKED)
        total_bounced = sum(1 for e in emails if e.status == EmailStatus.BOUNCED)
        
        open_rate = (total_opened / total_sent) * 100 if total_sent > 0 else 0
        click_rate = (total_clicked / total_sent) * 100 if total_sent > 0 else 0
        bounce_rate = (total_bounced / total_sent) * 100 if total_sent > 0 else 0
        
        # 按國家分析
        country_stats = {}
        for email in emails:
            country = email.supplier.country or "Unknown"
            if country not in country_stats:
                country_stats[country] = {"sent": 0, "opened": 0, "clicked": 0}
            
            country_stats[country]["sent"] += 1
            if email.status in [EmailStatus.OPENED, EmailStatus.CLICKED]:
                country_stats[country]["opened"] += 1
            if email.status == EmailStatus.CLICKED:
                country_stats[country]["clicked"] += 1
        
        # 計算各國家的打開率
        for country, stats in country_stats.items():
            if stats["sent"] > 0:
                stats["open_rate"] = round((stats["opened"] / stats["sent"]) * 100, 2)
                stats["click_rate"] = round((stats["clicked"] / stats["sent"]) * 100, 2)
        
        return {
            "period": "7 days",
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "total_sent": total_sent,
            "total_opened": total_opened,
            "total_clicked": total_clicked,
            "total_bounced": total_bounced,
            "open_rate": round(open_rate, 2),
            "click_rate": round(click_rate, 2),
            "bounce_rate": round(bounce_rate, 2),
            "by_country": country_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def generate_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        基於分析生成優化建議
        
        Args:
            analysis: 性能分析結果
            
        Returns:
            優化建議列表
        """
        suggestions = []
        
        # 打開率優化
        if analysis.get("open_rate", 0) < 20:
            suggestions.append({
                "type": "subject_optimization",
                "priority": "high",
                "title": "提高郵件打開率",
                "description": "當前打開率較低，建議優化主題行",
                "actions": [
                    "使用更具體的主題行",
                    "添加數字或特殊字符",
                    "測試不同主題行角度"
                ]
            })
        
        # 點擊率優化
        if analysis.get("click_rate", 0) < 5:
            suggestions.append({
                "type": "content_optimization",
                "priority": "high",
                "title": "提高郵件點擊率",
                "description": "內容未能有效吸引點擊",
                "actions": [
                    "改進行動號召 (CTA)",
                    "增加緊迫感",
                    "測試不同內容策略"
                ]
            })
        
        # 退信率優化
        if analysis.get("bounce_rate", 0) > 2:
            suggestions.append({
                "type": "list_quality",
                "priority": "high",
                "title": "降低退信率",
                "description": "退信率過高可能影響發送聲譽",
                "actions": [
                    "清理無效郵箱",
                    "驗證所有新郵箱",
                    "降低新郵箱的發送比例"
                ]
            })
        
        # 按國家優化
        country_stats = analysis.get("by_country", {})
        for country, stats in country_stats.items():
            if stats.get("sent", 0) >= 10:
                if stats.get("open_rate", 0) < 15:
                    suggestions.append({
                        "type": "timing_optimization",
                        "priority": "medium",
                        "title": f"優化 {country} 的發送時間",
                        "description": f"{country} 的打開率低於平均水平",
                        "actions": [
                            "調整發送時區",
                            "測試不同工作日",
                            "考慮當地工作時間"
                        ]
                    })
        
        return suggestions
    
    def apply_optimizations(self, suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        應用優化建議
        
        Args:
            suggestions: 優化建議列表
            
        Returns:
            應用結果
        """
        applied = []
        
        for suggestion in suggestions:
            if suggestion.get("priority") in ["high", "medium"]:
                # 創建學習模式
                pattern = LearningPattern(
                    owner_id=self.user_id,
                    pattern_type=suggestion["type"],
                    pattern_name=suggestion["title"],
                    description=suggestion["description"],
                    trigger_conditions={"auto_generated": True},
                    strategy={
                        "actions": suggestion.get("actions", []),
                        "priority": suggestion.get("priority"),
                    },
                    confidence=0.5,
                    is_active=True,
                )
                self.db.add(pattern)
                applied.append(suggestion["title"])
        
        self.db.commit()
        
        return {
            "applied_count": len(applied),
            "applied": applied
        }
    
    def learn_from_campaign(self, campaign: Campaign) -> List[Dict[str, Any]]:
        """
        從單個活動學習模式
        
        Args:
            campaign: 活動對象
            
        Returns:
            學習到的模式列表
        """
        patterns = []
        
        # 獲取活動的郵件
        emails = self.db.query(Email).filter(
            Email.campaign_id == campaign.id
        ).all()
        
        if len(emails) < 5:
            return patterns
        
        # 分析主題行模式
        subjects = [e.subject for e in emails if e.subject]
        if subjects:
            # 提取常見模式
            common_prefixes = {}
            for subject in subjects:
                words = subject.split()
                if len(words) > 0:
                    prefix = words[0]
                    common_prefixes[prefix] = common_prefixes.get(prefix, 0) + 1
            
            if common_prefixes:
                most_common_prefix = max(common_prefixes, key=common_prefixes.get)
                patterns.append({
                    "pattern_type": "subject_optimization",
                    "pattern_name": f"Subject prefix: {most_common_prefix}",
                    "description": "最常用的主題行前綴",
                    "strategy": {
                        "prefix": most_common_prefix,
                        "usage_count": common_prefixes[most_common_prefix]
                    },
                    "success_rate": campaign.open_rate,
                    "sample_size": len(emails),
                    "confidence": min(len(emails) / 50, 1.0)
                })
        
        # 分析發送時間模式
        if emails:
            sent_hours = [e.sent_at.hour for e in emails if e.sent_at]
            if sent_hours:
                avg_hour = sum(sent_hours) / len(sent_hours)
                
                # 根據打開率計算時間效率
                opened_emails = [e for e in emails if e.status in [EmailStatus.OPENED, EmailStatus.CLICKED]]
                if opened_emails:
                    opened_hours = [e.sent_at.hour for e in opened_emails if e.sent_at]
                    if opened_hours:
                        avg_opened_hour = sum(opened_hours) / len(opened_hours)
                        
                        patterns.append({
                            "pattern_type": "timing_optimization",
                            "pattern_name": f"Best send hour: {int(avg_opened_hour)}",
                            "description": f"最佳發送時間為 {int(avg_opened_hour)}:00",
                            "strategy": {
                                "send_hour": int(avg_opened_hour),
                                "avg_hour": round(avg_hour, 1)
                            },
                            "success_rate": campaign.open_rate,
                            "sample_size": len(opened_hours),
                            "confidence": min(len(opened_hours) / 30, 1.0)
                        })
        
        return patterns
    
    def apply_pattern(self, pattern: LearningPattern) -> bool:
        """
        應用學習到的模式
        
        Args:
            pattern: 學習模式
            
        Returns:
            是否成功應用
        """
        try:
            strategy = pattern.strategy
            
            if pattern.pattern_type == "subject_optimization":
                # 更新默認模板主題
                default_template = self.db.query(EmailTemplate).filter(
                    EmailTemplate.owner_id == self.user_id,
                    EmailTemplate.is_default == True
                ).first()
                
                if default_template and strategy.get("prefix"):
                    new_subject = f"{strategy['prefix']} {default_template.subject_template}"
                    default_template.subject_template = new_subject.strip()
                    self.db.commit()
                    
            elif pattern.pattern_type == "timing_optimization":
                # 記錄優化應用
                logger.info(f"Applied timing pattern: {pattern.pattern_name}")
            
            pattern.is_applied = True
            pattern.times_applied += 1
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying pattern {pattern.id}: {str(e)}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """
        生成優化報告
        
        Returns:
            優化報告
        """
        # 獲取活動概覽
        campaigns = self.db.query(Campaign).filter(
            Campaign.owner_id == self.user_id
        ).all()
        
        # 獲取學習模式
        patterns = self.db.query(LearningPattern).filter(
            LearningPattern.owner_id == self.user_id,
            LearningPattern.is_active == True
        ).all()
        
        # 性能分析
        analysis = self.analyze_performance()
        
        # 生成建議
        suggestions = self.generate_suggestions(analysis)
        
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "period": "last 7 days",
            "performance": analysis,
            "campaigns_summary": {
                "total": len(campaigns),
                "active": sum(1 for c in campaigns if c.status == CampaignStatus.RUNNING),
                "completed": sum(1 for c in campaigns if c.status == CampaignStatus.COMPLETED),
                "total_sent": sum(c.emails_sent for c in campaigns)
            },
            "learning_patterns": {
                "active": len(patterns),
                "applied": sum(1 for p in patterns if p.is_applied)
            },
            "suggestions": suggestions,
            "next_steps": [s["title"] for s in suggestions if s["priority"] == "high"]
        }
    
    def predict_success_rate(
        self,
        supplier: Supplier,
        template: EmailTemplate
    ) -> float:
        """
        預測郵件成功率
        
        Args:
            supplier: 供應商對象
            template: 郵件模板
            
        Returns:
            預測的成功率 (0-1)
        """
        base_rate = 0.2  # 基準打開率 20%
        
        # 根據歷史數據調整
        country_patterns = self.db.query(LearningPattern).filter(
            LearningPattern.owner_id == self.user_id,
            LearningPattern.pattern_type == "timing_optimization",
            LearningPattern.trigger_conditions.contains(supplier.country or "")
        ).all()
        
        if country_patterns:
            avg_confidence = sum(p.confidence for p in country_patterns) / len(country_patterns)
            base_rate *= (1 + avg_confidence * 0.2)
        
        # 根據供應商質量調整
        if supplier.quality_score > 70:
            base_rate *= 1.2
        elif supplier.quality_score < 30:
            base_rate *= 0.8
        
        return min(max(base_rate, 0.05), 0.8)
    
    def recommend_template(self, supplier: Supplier) -> Optional[EmailTemplate]:
        """
        為供應商推薦最佳模板
        
        Args:
            supplier: 供應商對象
            
        Returns:
            推薦的模板或 None
        """
        # 獲取所有模板
        templates = self.db.query(EmailTemplate).filter(
            EmailTemplate.owner_id == self.user_id,
            EmailTemplate.is_active == True
        ).all()
        
        if not templates:
            return None
        
        # 根據歷史表現評分
        best_template = None
        best_score = 0
        
        for template in templates:
            # 獲取模板使用統計
            emails = self.db.query(Email).filter(
                Email.supplier_id == supplier.id
            ).all() if supplier.id else []
            
            # 簡化的評分邏輯
            score = template.usage_count * 0.1 + (1.0 if template.is_default else 0)
            
            if score > best_score:
                best_score = score
                best_template = template
        
        return best_template or templates[0]
