"""
Google Search Service - 企業搜索服務
支持按國家/地區搜索英國、加拿大、北歐企業
"""
import requests
from typing import Dict, Any, List, Optional
from loguru import logger
from app.core.config import settings


# 國家/地區對應的 Google 域名
COUNTRY_GL_MAP = {
    # 英國
    "UK": "uk",
    "United Kingdom": "uk",
    "GB": "uk",
    "England": "uk",
    "Scotland": "uk",
    "Wales": "uk",
    "Northern Ireland": "uk",
    
    # 加拿大
    "Canada": "ca",
    "CA": "ca",
    "Ontario": "ca",
    "Toronto": "ca",
    "Vancouver": "ca",
    "Montreal": "ca",
    
    # 北歐
    "Sweden": "se",
    "SE": "se",
    "Norway": "no",
    "NO": "no",
    "Denmark": "dk",
    "DK": "dk",
    "Finland": "fi",
    "FI": "fi",
    "Iceland": "is",
    "IS": "is",
    
    # 北歐擴展
    "Nordic": "se",
    "Scandinavia": "se",
}


class GoogleSearchService:
    """Google 企業搜索服務"""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_SEARCH_API_KEY
        self.search_engine_id = settings.GOOGLE_SEARCH_ENGINE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def _get_country_code(self, country: str) -> str:
        """獲取國家代碼"""
        return COUNTRY_GL_MAP.get(country, "us")
    
    def search_companies(
        self,
        query: str,
        country: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索企業
        
        Args:
            query: 搜索關鍵詞（如公司名稱、行業等）
            country: 國家/地區（UK, Canada, Sweden, Norway 等）
            limit: 返回結果數量
            
        Returns:
            企業搜索結果列表
        """
        if not self.api_key or not self.search_engine_id:
            logger.error("Google Search API key or Search Engine ID not configured")
            return []
        
        try:
            # 構建搜索查詢
            search_query = query
            if country:
                # 添加國家/地區到查詢
                country_name = country.lower()
                if country_name in ["uk", "united kingdom"]:
                    search_query = f"{query} UK company"
                elif country_name in ["canada", "ca"]:
                    search_query = f"{query} Canada company"
                elif country_name in ["sweden", "se"]:
                    search_query = f"{query} Sweden company"
                elif country_name in ["norway", "no"]:
                    search_query = f"{query} Norway company"
                elif country_name in ["denmark", "dk"]:
                    search_query = f"{query} Denmark company"
                elif country_name in ["finland", "fi"]:
                    search_query = f"{query} Finland company"
                elif country_name in ["nordic", "scandinavia"]:
                    search_query = f"{query} Nordic company"
            
            # API 參數
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": search_query,
                "num": min(limit, 10),  # Google API 最多返回 10 個
                "gl": self._get_country_code(country) if country else "us",  # 地理位置
                "hl": "en",  # 語言為英語
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "display_link": item.get("displayLink", ""),
                })
            
            logger.info(f"Found {len(results)} results for query: {search_query}")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Google Search API error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error searching companies: {str(e)}")
            return []
    
    def search_uk_companies(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索英國企業"""
        return self.search_companies(query, country="UK", limit=limit)
    
    def search_canadian_companies(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索加拿大企業"""
        return self.search_companies(query, country="Canada", limit=limit)
    
    def search_nordic_companies(
        self,
        query: str,
        country: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索北歐企業
        
        Args:
            query: 搜索關鍵詞
            country: 具體國家（Sweden, Norway, Denmark, Finland）
            limit: 返回結果數量
        """
        if country and country in ["Sweden", "Norway", "Denmark", "Finland", "SE", "NO", "DK", "FI"]:
            return self.search_companies(query, country=country, limit=limit)
        
        # 搜索所有北歐國家
        all_results = []
        nordic_countries = ["Sweden", "Norway", "Denmark", "Finland"]
        
        for nordic_country in nordic_countries:
            results = self.search_companies(query, country=nordic_country, limit=limit)
            all_results.extend(results)
        
        # 去重
        seen_links = set()
        unique_results = []
        for result in all_results:
            if result["link"] not in seen_links:
                seen_links.add(result["link"])
                unique_results.append(result)
        
        return unique_results[:limit]
    
    def search_by_industry(
        self,
        industry: str,
        country: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        按行業搜索企業
        
        Args:
            industry: 行業關鍵詞
            country: 國家
            limit: 返回結果數量
        """
        query = f"{industry} wholesale distributor"
        return self.search_companies(query, country=country, limit=limit)


# 全局實例
google_search_service = GoogleSearchService()
