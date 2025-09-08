import asyncio
import json
import logging
from typing import Dict, List, Set, Optional
from playwright.async_api import Page, Response

from models import ExploitData
from config import Config
from utils import DataUtils


class APIHandler: 
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.api_responses: List[Dict] = []
        self.processed_urls: Set[str] = set()
        self.unique_exploits: Set[str] = set()
        self.all_exploits: List[ExploitData] = []
        
    async def setup_api_interception(self, page: Page):     
        # Intercept network responses to capture API data   
        async def handle_response(response: Response):
            try:
                url = response.url
                
                # Intercept only the search API of sploitus
                if Config.SEARCH_API_PATH in url and response.status == 200:
                    self.logger.info(f"Intercepted API response: {url}")
                    
                    await self._process_api_response(response)
                    
            except Exception as e:
                self.logger.error(f"Error handling response: {e}")
        
        page.on("response", handle_response)
        self.logger.info("API interception set up")
    
    async def _process_api_response(self, response: Response):
        try:
            response_text = await response.text()
            if not response_text:
                return
            
            response_data = json.loads(response_text)
            
            if not isinstance(response_data, dict):
                return
            
            exploits_data = response_data.get('exploits', [])
            if not exploits_data:
                self.logger.warning("No 'exploits' field found in API response")
                return
            
            new_exploits = []
            for item in exploits_data:
                exploit = self._parse_exploit_data(item)
                if exploit and exploit.get_hash() not in self.unique_exploits:
                    self.unique_exploits.add(exploit.get_hash())
                    new_exploits.append(exploit)
            
            self.all_exploits.extend(new_exploits)
            
            self.logger.info(f"Processed API response: {len(new_exploits)} new exploits "
                           f"(Total: {len(self.all_exploits)})")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
        except Exception as e:
            self.logger.error(f"Error processing API response: {e}")
    
    def _parse_exploit_data(self, item: Dict) -> Optional[ExploitData]:
        try:
            title = item.get('title', '')
            if not title:
                return None
            
            id = item.get('id', '')
            if not id:
                return None
            
            published_raw = item.get('published', '')
            published = DataUtils.extract_date(published_raw)
            
            source = item.get('source', '')
            score = item.get('score', None)
            type = item.get('type', '')
            language = item.get('language', None)
            href = item.get('href', None)
            
            return ExploitData(
                id=id,
                title=title,
                published=published,
                score=score,
                href=href,
                type=type,
                source=source,
                language=language
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing exploit data: {e}")
            return None
    
    def get_all_exploits(self) -> List[ExploitData]:
        return self.all_exploits
    
    def get_exploit_count(self) -> int:
        return len(self.all_exploits)
