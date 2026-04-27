"""
Writer Agent - 郵件撰寫代理
負責分析產品資訊並生成個性化銷售郵件
"""
import os
import json
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from openai import OpenAI
from loguru import logger
from app.core.config import settings
from app.models.supplier import Supplier
from app.models.email import EmailTemplate
from app.models.campaign import Campaign
from app.models.learning_pattern import LearningPattern


class WriterAgent:
    """Writer Agent - AI 郵件生成"""
    
    def __init__(self, user_id: int, db: Session):
        self.user_id = user_id
        self.db = db
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.model = settings.OPENAI_MODEL
    
    def _get_system_prompt(self) -> str:
        """獲取系統提示詞"""
        return """你是一個專業的 B2B 銷售郵件撰寫專家。

你的職責是：
1. 分析供應商的產品和業務資訊
2. 撰寫引人注目的個性化銷售郵件
3. 確保郵件內容專業、有說服力且不會被視為垃圾郵件

郵件撰寫原則：
- 主題行：簡潔有力，吸引注意力，不超過 60 個字符
- 開場白：直接說明價值主張，不要過度寒暄
- 內容：突出我們能為對方帶來什麼價值
- 行動號召：明確說明下一步
- 簽名：專業且可信

避免：
- 過度使用感嘆號
- 全大寫字母
- 明確的推銷語氣
- 可識別的模板化語言
- 承諾無法兌現的價值

每封郵件都應該像是專門為這個收件人撰寫的。"""
    
    def _build_email_context(
        self,
        supplier: Supplier,
        campaign: Optional[Campaign] = None
    ) -> Dict[str, Any]:
        """
        構建郵件上下文
        
        Args:
            supplier: 供應商對象
            campaign: 可選的活動對象
            
        Returns:
            上下文字典
        """
        context = {
            "supplier_name": supplier.company_name,
            "supplier_country": supplier.country or "your country",
            "supplier_city": supplier.city or "",
            "supplier_business_type": supplier.business_type or "business",
            "supplier_products": ", ".join(supplier.product_categories) if supplier.product_categories else "",
            "supplier_description": supplier.description or "",
            "supplier_website": supplier.website or "",
        }
        
        if campaign:
            context.update({
                "campaign_name": campaign.name,
                "campaign_description": campaign.description or "",
            })
        
        return context
    
    def _render_template(
        self,
        template: EmailTemplate,
        variables: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        渲染郵件模板
        
        Args:
            template: 郵件模板
            variables: 變量字典
            
        Returns:
            渲染後的主題和正文
        """
        subject = template.subject_template
        body = template.body_template
        
        # 替換變量
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            subject = subject.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))
        
        # 生成純文本版本
        import re
        body_text = re.sub(r'<[^>]+>', '', body)  # 移除 HTML 標籤
        body_text = re.sub(r'\s+', ' ', body_text)  # 合併空白
        body_text = body_text.strip()
        
        return {
            "subject": subject,
            "body": body,
            "body_text": body_text
        }
    
    def generate_personalized_email(
        self,
        template: EmailTemplate,
        supplier: Supplier,
        campaign: Optional[Campaign] = None
    ) -> Dict[str, str]:
        """
        生成個性化郵件
        
        Args:
            template: 郵件模板
            supplier: 供應商對象
            campaign: 可選的活動對象
            
        Returns:
            包含 subject, body, body_text 的字典
        """
        # 首先嘗試模板渲染
        context = self._build_email_context(supplier, campaign)
        rendered = self._render_template(template, context)
        
        # 如果有 AI 可用，使用 AI 進一步個性化
        if self.client:
            try:
                ai_content = self._generate_with_ai(
                    supplier=supplier,
                    base_subject=rendered["subject"],
                    base_body=rendered["body"]
                )
                
                if ai_content:
                    return ai_content
            except Exception as e:
                logger.warning(f"AI personalization failed, using template: {str(e)}")
        
        return rendered
    
    def _generate_with_ai(
        self,
        supplier: Supplier,
        base_subject: str,
        base_body: str
    ) -> Optional[Dict[str, str]]:
        """
        使用 AI 生成個性化郵件
        
        Args:
            supplier: 供應商對象
            base_subject: 基礎主題
            base_body: 基礎正文
            
        Returns:
            個性化後的郵件或 None
        """
        if not self.client:
            return None
        
        try:
            # 構建提示詞
            context = f"""
公司名稱: {supplier.company_name}
國家: {supplier.country or "未知"}
城市: {supplier.city or "未知"}
企業類型: {supplier.business_type or "未知"}
產品類別: {", ".join(supplier.product_categories) if supplier.product_categories else "未知"}
公司描述: {supplier.description or "未知"}
網站: {supplier.website or "未知"}

基礎主題: {base_subject}
基礎正文: {base_body[:500]}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": f"""請根據以下供應商資訊，優化並個性化以下郵件：

{context}

要求：
1. 保持基礎主題的核心信息，但可以更個性化
2. 根據供應商的產品和業務調整正文內容
3. 確保郵件看起來像是專門為這個供應商撰寫的
4. 不要添加任何[公司名]之類的佔位符

請返回以下格式的 JSON：
{{
    "subject": "優化後的主題行",
    "body": "優化後的 HTML 正文"
}}
"""}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # 解析 JSON 回應
            # 嘗試提取 JSON 部分
            import re
            json_match = re.search(r'\{[^{}]*"subject"[^{}]*"body"[^{}]*\}', content, re.DOTALL)
            if json_match:
                email_data = json.loads(json_match.group())
                
                # 生成純文本版本
                import re
                body_text = re.sub(r'<[^>]+>', '', email_data.get("body", ""))
                body_text = re.sub(r'\s+', ' ', body_text).strip()
                
                return {
                    "subject": email_data.get("subject", base_subject),
                    "body": email_data.get("body", base_body),
                    "body_text": body_text
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating with AI: {str(e)}")
            return None
    
    def generate_ab_variant(
        self,
        template: EmailTemplate,
        supplier: Supplier
    ) -> Dict[str, str]:
        """
        生成 A/B 測試變體
        
        Args:
            template: 原始模板
            supplier: 供應商對象
            
        Returns:
            B 變體的 subject 和 body
        """
        if not self.client:
            return {
                "subject": template.variant_b_subject or template.subject_template,
                "body": template.variant_b_body or template.body_template
            }
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一個專業的 A/B 測試郵件撰寫專家。"},
                    {"role": "user", "content": f"""請為以下郵件創建一個 A/B 測試變體：

原始主題: {template.subject_template}
原始正文: {template.body_template[:500]}

目標公司: {supplier.company_name}

請創建一個與原始版本不同風格的變體，可以：
- 嘗試不同的主題行角度
- 使用不同的開場方式
- 強調不同的價值主張

請返回以下格式的 JSON：
{{
    "subject": "變體 B 的主題行",
    "body": "變體 B 的 HTML 正文"
}}
"""}
                ],
                temperature=0.9,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            
            import re
            json_match = re.search(r'\{[^{}]*"subject"[^{}]*"body"[^{}]*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
        except Exception as e:
            logger.error(f"Error generating A/B variant: {str(e)}")
        
        return {
            "subject": template.variant_b_subject or template.subject_template,
            "body": template.variant_b_body or template.body_template
        }
    
    def analyze_product(self, product_description: str) -> Dict[str, Any]:
        """
        分析產品描述
        
        Args:
            product_description: 產品描述
            
        Returns:
            分析結果
        """
        if not self.client:
            return {
                "category": None,
                "keywords": [],
                "value_proposition": None,
                "target_audience": None
            }
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一個專業的 B2B 市場分析師。"},
                    {"role": "user", "content": f"""請分析以下產品描述：

{product_description}

請返回以下格式的 JSON：
{{
    "category": "產品類別",
    "keywords": ["關鍵詞1", "關鍵詞2", "關鍵詞3"],
    "value_proposition": "價值主張",
    "target_audience": "目標受眾描述"
}}
"""}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            import re
            json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
        except Exception as e:
            logger.error(f"Error analyzing product: {str(e)}")
        
        return {
            "category": None,
            "keywords": [],
            "value_proposition": None,
            "target_audience": None
        }
    
    def generate_subject_line(
        self,
        supplier: Supplier,
        base_subject: str
    ) -> List[str]:
        """
        生成多個主題行備選
        
        Args:
            supplier: 供應商對象
            base_subject: 基礎主題
            
        Returns:
            主題行列表
        """
        if not self.client:
            return [base_subject]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一個專業的郵件主題行撰寫專家。"},
                    {"role": "user", "content": f"""請為以下郵件生成 3 個不同風格的主題行：

目標公司: {supplier.company_name}
國家: {supplier.country}
產品: {", ".join(supplier.product_categories) if supplier.product_categories else "未知"}
基礎主題: {base_subject}

要求：
1. 每個主題行不超過 60 個字符
2. 三個主題要有不同的角度（疑問型、數字型、價值型等）
3. 確保每個主題都吸引人且與目標公司相關

請返回以下格式的 JSON：
{{
    "subjects": ["主題1", "主題2", "主題3"]
}}
"""}
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            
            import re
            json_match = re.search(r'\[[^\]]*\]', content)
            if json_match:
                return json.loads(json_match.group())
            
        except Exception as e:
            logger.error(f"Error generating subject lines: {str(e)}")
        
        return [base_subject]
    
    def optimize_timing(self, supplier: Supplier) -> Dict[str, Any]:
        """
        優化發送時間
        
        Args:
            supplier: 供應商對象
            
        Returns:
            建議的發送時間
        """
        # 根據供應商所在時區建議最佳發送時間
        timezone_map = {
            "UK": {"hour": 9, "day": [1, 2, 3, 4, 5]},  # 英國時間
            "United Kingdom": {"hour": 9, "day": [1, 2, 3, 4, 5]},
            "US": {"hour": 10, "day": [2, 3, 4]},  # 美國時間
            "USA": {"hour": 10, "day": [2, 3, 4]},
            "China": {"hour": 9, "day": [1, 2, 3, 4, 5]},
        }
        
        country = supplier.country or ""
        for key, value in timezone_map.items():
            if key.lower() in country.lower():
                return {
                    "suggested_hour": value["hour"],
                    "suggested_days": value["day"],
                    "timezone": key
                }
        
        # 默認時間
        return {
            "suggested_hour": 9,
            "suggested_days": [1, 2, 3, 4, 5],
            "timezone": "UTC"
        }
