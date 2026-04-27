"""
Agent 測試
"""
import pytest
from unittest.mock import MagicMock, patch
from app.agents.scout_agent import ScoutAgent
from app.agents.writer_agent import WriterAgent


class TestScoutAgent:
    """Scout Agent 測試"""
    
    def test_verify_supplier_valid(self):
        """測試驗證有效供應商"""
        # Mock 數據庫會話
        db = MagicMock()
        
        # Mock 供應商
        supplier = MagicMock()
        supplier.company_name = "Test Company"
        supplier.email = "contact@test.com"
        supplier.website = "https://test.com"
        supplier.phone = "+1234567890"
        supplier.address = "123 Test St"
        supplier.city = "London"
        supplier.country = "UK"
        supplier.description = "A test company"
        supplier.certifications = ["ISO9001"]
        
        agent = ScoutAgent(user_id=1, db=db)
        result = agent.verify_supplier(supplier)
        
        assert result["status"].value in ["verified", "pending"]
        assert "quality_score" in result
    
    def test_verify_supplier_missing_name(self):
        """測試驗證缺少名稱的供應商"""
        db = MagicMock()
        
        supplier = MagicMock()
        supplier.company_name = None
        
        agent = ScoutAgent(user_id=1, db=db)
        result = agent.verify_supplier(supplier)
        
        assert result["status"].value == "invalid"
        assert "公司名稱" in result.get("notes", "")
    
    def test_validate_email_valid(self):
        """測試驗證有效郵箱"""
        db = MagicMock()
        agent = ScoutAgent(user_id=1, db=db)
        
        assert agent.validate_email("contact@company.co.uk") == True
        assert agent.validate_email("user@business.com") == True
    
    def test_validate_email_invalid(self):
        """測試驗證無效郵箱"""
        db = MagicMock()
        agent = ScoutAgent(user_id=1, db=db)
        
        assert agent.validate_email("invalid") == False
        assert agent.validate_email("user@mailinator.com") == False


class TestWriterAgent:
    """Writer Agent 測試"""
    
    def test_render_template(self):
        """測試模板渲染"""
        db = MagicMock()
        agent = WriterAgent(user_id=1, db=db)
        
        # Mock 模板
        template = MagicMock()
        template.subject_template = "Hello {{supplier_name}}"
        template.body_template = "<p>Welcome to {{supplier_country}}</p>"
        
        variables = {
            "supplier_name": "Test Company",
            "supplier_country": "UK"
        }
        
        result = agent._render_template(template, variables)
        
        assert result["subject"] == "Hello Test Company"
        assert "UK" in result["body"]
    
    def test_build_email_context(self):
        """測試構建郵件上下文"""
        db = MagicMock()
        agent = WriterAgent(user_id=1, db=db)
        
        # Mock 供應商
        supplier = MagicMock()
        supplier.company_name = "Test Supplier"
        supplier.country = "UK"
        supplier.city = "London"
        supplier.business_type = "wholesaler"
        supplier.product_categories = ["Electronics", "Gadgets"]
        supplier.description = "A tech supplier"
        supplier.website = "https://test.com"
        
        context = agent._build_email_context(supplier)
        
        assert context["supplier_name"] == "Test Supplier"
        assert context["supplier_country"] == "UK"
        assert "Electronics" in context["supplier_products"]
