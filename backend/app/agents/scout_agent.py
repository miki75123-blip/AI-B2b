"""
Scout Agent - 爬蟲代理
負責從 B2B 平台自動爬取供應商資訊
"""
import asyncio
import httpx
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup
from loguru import logger
from app.core.config import settings
from app.models.supplier import Supplier, SourcePlatform, VerificationStatus
import re
from urllib.parse import urljoin

# 可選依賴：Playwright（如果未安裝則回退到 HTTP 客戶端）
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed, using HTTP client only")


class ScoutAgent:
    """Scout Agent - 瀏覽器自動化與數據採集"""
    
    def __init__(self, user_id: int, db: Session):
        self.user_id = user_id
        self.db = db
        self.headers = {
            "User-Agent": settings.SCRAPER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
    
    async def _fetch_with_browser(self, url: str) -> Optional[str]:
        """
        使用瀏覽器獲取頁面內容（如果 Playwright 可用）
        否則回退到 HTTP 客戶端
        
        Args:
            url: 頁面 URL
            
        Returns:
            HTML 內容或 None
        """
        # 如果 Playwright 不可用，回退到 HTTP 客戶端
        if not PLAYWRIGHT_AVAILABLE:
            return await self._fetch_with_client(url)
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                try:
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    await asyncio.sleep(settings.SCRAPER_DELAY_SECONDS)
                    content = await page.content()
                    return content
                except Exception as e:
                    logger.error(f"Error fetching {url}: {str(e)}")
                    return None
                finally:
                    await browser.close()
        except Exception as e:
            logger.error(f"Playwright error, falling back to HTTP client: {str(e)}")
            return await self._fetch_with_client(url)
    
    async def _fetch_with_client(self, url: str) -> Optional[str]:
        """
        使用 HTTP 客戶端獲取頁面內容
        
        Args:
            url: 頁面 URL
            
        Returns:
            HTML 內容或 None
        """
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.error(f"Error fetching {url}: {str(e)}")
                return None
    
    def _parse_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        從文本中解析聯繫資訊
        
        Args:
            text: 文本內容
            
        Returns:
            聯繫資訊字典
        """
        result = {
            "email": None,
            "phone": None,
        }
        
        # 郵箱正則
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            # 過濾通用郵箱
            valid_emails = [e for e in emails if not any(
                skip in e.lower() for skip in ['example.com', 'test.com', 'domain.com']
            )]
            if valid_emails:
                result["email"] = valid_emails[0]
        
        # 電話正則
        phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,}'
        phones = re.findall(phone_pattern, text)
        if phones:
            # 清理並選擇最可能的電話
            cleaned = [p.strip() for p in phones if len(p.strip()) >= 8]
            if cleaned:
                result["phone"] = cleaned[0]
        
        return result
    
    def scrape_esources(self, url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        爬取 eSources.co.uk
        
        Args:
            url: 可選的特定 URL
            
        Returns:
            供應商數據列表
        """
        if url:
            return self._scrape_esources_listing(url)
        
        # 默認 URL
        base_url = "https://www.esources.co.uk/suppliers/"
        categories = [
            "wholesale-gifts",
            "wholesale-fashion",
            "wholesale-electronics",
            "wholesale-home",
        ]
        
        results = []
        for category in categories:
            listing_url = f"{base_url}{category}/"
            try:
                suppliers = asyncio.run(self._scrape_esources_listing(listing_url))
                results.extend(suppliers)
            except Exception as e:
                logger.error(f"Error scraping eSources category {category}: {str(e)}")
        
        return results
    
    def _scrape_esources_listing(self, url: str) -> List[Dict[str, Any]]:
        """爬取 eSources 列表頁"""
        results = []
        
        try:
            html = asyncio.run(self._fetch_with_client(url))
            if not html:
                return results
            
            soup = BeautifulSoup(html, "lxml")
            
            # 查找供應商卡片
            cards = soup.select(".supplier-card, .listing-item, article")
            
            for card in cards:
                try:
                    company_name_elem = card.select_one("h2, h3, .company-name, .title")
                    if not company_name_elem:
                        continue
                    
                    company_name = company_name_elem.get_text(strip=True)
                    
                    # 獲取詳情 URL
                    detail_link = card.select_one("a[href]")
                    detail_url = urljoin(url, detail_link["href"]) if detail_link else None
                    
                    # 基本資訊
                    supplier_data = {
                        "company_name": company_name,
                        "source_url": detail_url,
                        "source_page_title": company_name,
                        "raw_data": str(card),
                    }
                    
                    # 如果有詳情頁，稍後可以進一步爬取
                    if detail_url:
                        supplier_data["website"] = detail_url
                    
                    results.append(supplier_data)
                    
                except Exception as e:
                    logger.error(f"Error parsing eSources card: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping eSources listing {url}: {str(e)}")
        
        return results
    
    def scrape_creoate(self, url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        爬取 Creoate.com
        
        Args:
            url: 可選的特定 URL
            
        Returns:
            供應商數據列表
        """
        if url:
            return self._scrape_creoate_listing(url)
        
        # 默認 URL
        base_url = "https://creoate.com/suppliers"
        
        try:
            return self._scrape_creoate_listing(base_url)
        except Exception as e:
            logger.error(f"Error scraping Creoate: {str(e)}")
            return []
    
    def _scrape_creoate_listing(self, url: str) -> List[Dict[str, Any]]:
        """爬取 Creoate 列表頁"""
        results = []
        
        try:
            html = asyncio.run(self._fetch_with_browser(url))
            if not html:
                return results
            
            soup = BeautifulSoup(html, "lxml")
            
            # 查找供應商卡片
            cards = soup.select(".supplier-card, .vendor-card, [data-supplier-id]")
            
            for card in cards:
                try:
                    company_name_elem = card.select_one("h2, h3, .name, .company-name")
                    if not company_name_elem:
                        continue
                    
                    company_name = company_name_elem.get_text(strip=True)
                    
                    # 獲取詳情 URL
                    detail_link = card.select_one("a[href]")
                    detail_url = urljoin(url, detail_link["href"]) if detail_link else None
                    
                    # 聯繫資訊
                    contact_text = card.get_text()
                    contact_info = self._parse_contact_info(contact_text)
                    
                    supplier_data = {
                        "company_name": company_name,
                        "source_url": detail_url,
                        "source_page_title": company_name,
                        "email": contact_info.get("email"),
                        "phone": contact_info.get("phone"),
                        "raw_data": str(card),
                    }
                    
                    if detail_url:
                        supplier_data["website"] = detail_url
                    
                    results.append(supplier_data)
                    
                except Exception as e:
                    logger.error(f"Error parsing Creoate card: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping Creoate listing {url}: {str(e)}")
        
        return results
    
    def scrape_thewholesaler(self, url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        爬取 TheWholesaler.co.uk
        
        Args:
            url: 可選的特定 URL
            
        Returns:
            供應商數據列表
        """
        if url:
            return self._scrape_thewholesaler_listing(url)
        
        # 默認 URL
        base_url = "https://www.thewholesaler.co.uk"
        categories = [
            "/wholesale-gifts",
            "/wholesale-jewellery",
            "/wholesale-toys",
            "/wholesale-electrical",
        ]
        
        results = []
        for category in categories:
            listing_url = f"{base_url}{category}"
            try:
                suppliers = self._scrape_thewholesaler_listing(listing_url)
                results.extend(suppliers)
            except Exception as e:
                logger.error(f"Error scraping TheWholesaler category {category}: {str(e)}")
        
        return results
    
    def _scrape_thewholesaler_listing(self, url: str) -> List[Dict[str, Any]]:
        """爬取 TheWholesaler 列表頁"""
        results = []
        
        try:
            html = asyncio.run(self._fetch_with_client(url))
            if not html:
                return results
            
            soup = BeautifulSoup(html, "lxml")
            
            # 查找供應商列表
            items = soup.select(".supplier-listing, .wholesaler-item, .listing-row")
            
            for item in items:
                try:
                    company_name_elem = item.select_one("h2, h3, .company-name, .name")
                    if not company_name_elem:
                        continue
                    
                    company_name = company_name_elem.get_text(strip=True)
                    
                    # 獲取詳情 URL
                    detail_link = item.select_one("a[href]")
                    detail_url = urljoin(url, detail_link["href"]) if detail_link else None
                    
                    # 地點
                    location_elem = item.select_one(".location, .address, .city")
                    country = location_elem.get_text(strip=True) if location_elem else None
                    
                    supplier_data = {
                        "company_name": company_name,
                        "source_url": detail_url,
                        "source_page_title": company_name,
                        "country": country,
                        "raw_data": str(item),
                    }
                    
                    if detail_url:
                        supplier_data["website"] = detail_url
                    
                    results.append(supplier_data)
                    
                except Exception as e:
                    logger.error(f"Error parsing TheWholesaler item: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping TheWholesaler listing {url}: {str(e)}")
        
        return results
    
    def verify_supplier(self, supplier: Supplier) -> Dict[str, Any]:
        """
        驗證供應商
        
        Args:
            supplier: 供應商對象
            
        Returns:
            驗證結果
        """
        result = {
            "status": VerificationStatus.PENDING,
            "notes": None,
            "quality_score": 0,
            "verified_at": None,
        }
        
        try:
            # 檢查必填欄位
            if not supplier.company_name:
                result["status"] = VerificationStatus.INVALID
                result["notes"] = "缺少公司名稱"
                return result
            
            # 檢查郵箱格式
            if supplier.email:
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                if not re.match(email_pattern, supplier.email):
                    result["status"] = VerificationStatus.INVALID
                    result["notes"] = "郵箱格式無效"
                    return result
            
            # 計算質量分數
            score = 0
            
            # 有網站 +20
            if supplier.website:
                score += 20
            
            # 有郵箱 +20
            if supplier.email:
                score += 20
            
            # 有電話 +15
            if supplier.phone:
                score += 15
            
            # 有完整地址 +15
            if supplier.address and supplier.city and supplier.country:
                score += 15
            
            # 有描述 +15
            if supplier.description:
                score += 15
            
            # 有認證 +15
            if supplier.certifications:
                score += 15
            
            result["quality_score"] = score
            
            # 設置驗證狀態
            if score >= 50:
                result["status"] = VerificationStatus.VERIFIED
                result["notes"] = "驗證通過"
            else:
                result["status"] = VerificationStatus.PENDING
                result["notes"] = "信息不完整，需要補充"
            
            from datetime import datetime
            result["verified_at"] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error verifying supplier {supplier.id}: {str(e)}")
            result["status"] = VerificationStatus.INVALID
            result["notes"] = f"驗證過程出錯: {str(e)}"
        
        return result
    
    def validate_email(self, email: str) -> bool:
        """
        驗證郵箱是否有效
        
        Args:
            email: 郵箱地址
            
        Returns:
            是否有效
        """
        # 基本格式檢查
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.match(email_pattern, email):
            return False
        
        # 檢查是否是通用/一次性郵箱
        disposable_domains = [
            "tempmail.com", "throwaway.com", "mailinator.com",
            "guerrillamail.com", "10minutemail.com", "fakeinbox.com"
        ]
        
        domain = email.split("@")[1].lower()
        if any(d in domain for d in disposable_domains):
            return False
        
        return True
