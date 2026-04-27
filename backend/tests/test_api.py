"""
API 測試
"""
import pytest
from fastapi import status


class TestAuth:
    """認證 API 測試"""
    
    def test_register(self, client):
        """測試用戶註冊"""
        response = client.post("/api/auth/register", json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New User"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
    
    def test_login(self, client):
        """測試用戶登入"""
        # 先註冊
        client.post("/api/auth/register", json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "password123"
        })
        
        # 登入
        response = client.post("/api/auth/login", data={
            "username": "loginuser",
            "password": "password123"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client):
        """測試無效憑證"""
        response = client.post("/api/auth/login", data={
            "username": "nonexistent",
            "password": "wrongpass"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSuppliers:
    """供應商 API 測試"""
    
    def test_list_suppliers_empty(self, client, auth_headers):
        """測試空供應商列表"""
        response = client.get("/api/suppliers/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert data["total"] == 0
    
    def test_create_supplier(self, client, auth_headers):
        """測試創建供應商"""
        response = client.post("/api/suppliers/", headers=auth_headers, json={
            "company_name": "Test Supplier Ltd",
            "email": "contact@test.com",
            "country": "UK",
            "business_type": "wholesaler"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["company_name"] == "Test Supplier Ltd"
        assert data["country"] == "UK"
    
    def test_get_supplier(self, client, auth_headers):
        """測試獲取供應商詳情"""
        # 先創建
        create_response = client.post("/api/suppliers/", headers=auth_headers, json={
            "company_name": "Detail Test Supplier"
        })
        supplier_id = create_response.json()["id"]
        
        # 獲取詳情
        response = client.get(f"/api/suppliers/{supplier_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["company_name"] == "Detail Test Supplier"


class TestCampaigns:
    """活動 API 測試"""
    
    def test_list_campaigns_empty(self, client, auth_headers):
        """測試空活動列表"""
        response = client.get("/api/campaigns/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_create_campaign(self, client, auth_headers):
        """測試創建活動"""
        response = client.post("/api/campaigns/", headers=auth_headers, json={
            "name": "Test Campaign",
            "description": "A test marketing campaign",
            "daily_send_limit": 50,
            "total_send_limit": 1000
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Campaign"
        assert data["status"] == "draft"


class TestDashboard:
    """儀表板 API 測試"""
    
    def test_get_dashboard(self, client, auth_headers):
        """測試獲取儀表板數據"""
        response = client.get("/api/dashboard/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "supplier_stats" in data
        assert "email_stats" in data
        assert "campaign_stats" in data
