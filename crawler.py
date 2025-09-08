import asyncio
import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from playwright.async_api import async_playwright
import httpx

from config import Config
from models import ExploitData
from api_handler import APIHandler
from utils import BrowserUtils, FileUtils, DataUtils


class SploitusCrawler:    
    def __init__(self):
        Config.create_directories()
        self.setup_logging()
        self.cookies = ""
        self.all_exploits: List[ExploitData] = []
        
    def setup_logging(self):
        log_level = getattr(Config, 'LOG_LEVEL', 'INFO')
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        
        logging.basicConfig(
            level=numeric_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Config.LOG_FILE, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def _get_cookies_with_playwright(self, query: str = "Rce") -> str:
        self.logger.info("Getting cookies using Playwright...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=Config.HEADLESS_MODE,
                args=Config.BROWSER_ARGS
            )
            
            page = await browser.new_page()
            
            # Navigate to the site and bypass Cloudflare
            url = f"https://sploitus.com/?query={query}#exploits"
            timeout = getattr(Config, 'PAGE_TIMEOUT', 60000)
            await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
            
            await BrowserUtils.bypass_cloudflare(page, self.logger)
            
            # Get cookies
            cookies = await page.context.cookies()
            cookie_string = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
            
            self.logger.info(f"Successfully obtained {len(cookies)} cookies")
            
            await browser.close()
            return cookie_string

    def _build_headers(self, cookie: str, query: str) -> Dict[str, str]:
        return {
            "Host": "sploitus.com",
            "Cookie": cookie.strip(),
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json",
            "Sec-Ch-Ua": "\"Chromium\";v=\"133\", \"Not(A:Brand\";v=\"99\"",
            "Content-Type": "application/json",
            "Sec-Ch-Ua-Mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/133.0.0.0 Safari/537.36",
            "Origin": "https://sploitus.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": f"https://sploitus.com/?query={query}",
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=1, i",
        }

    def post_with_retry(self, client: httpx.Client, url: str, headers: Dict[str, str], 
                       payload: Dict[str, Any], max_retries: int = 6, base_pause: float = 1.2) -> httpx.Response:
        attempt = 0
        while True:
            try:
                r = client.post(url, headers=headers, json=payload, timeout=30)
            except httpx.HTTPError as e:
                attempt += 1
                if attempt > max_retries:
                    raise
                time.sleep(base_pause * (2 ** (attempt - 1)))
                continue

            if r.status_code in (200, 201):
                return r

            # Handle Cloudflare/rate limit responses
            if r.status_code in (429, 403, 502, 503, 520, 521, 522, 523, 524):
                attempt += 1
                if attempt > max_retries:
                    r.raise_for_status()
                
                pause = base_pause * (2 ** (attempt - 1))
                try:
                    retry_after = float(r.headers.get("Retry-After", "0"))
                    pause = max(pause, retry_after)
                except ValueError:
                    pass
                
                self.logger.warning(f"Rate limited (status {r.status_code}), retrying in {pause}s...")
                time.sleep(pause)
                continue

            # Other errors
            r.raise_for_status()

    def fetch_page(self, client: httpx.Client, query: str, offset: int, 
                   typ: str = "exploits", sort: str = "default", title_flag: bool = False) -> Dict[str, Any]:
        url = "https://sploitus.com/search"
        headers = self._build_headers(cookie=self.cookies, query=query)
        payload = {
            "type": typ,
            "sort": sort,
            "query": query,
            "title": title_flag,
            "offset": offset,
        }
        
        resp = self.post_with_retry(client, url, headers, payload)
        try:
            return resp.json()
        except json.JSONDecodeError:
            return {"_non_json_body": resp.text, "_status": resp.status_code}

    def parse_exploit_data(self, item: Dict) -> ExploitData:
        return ExploitData(
            id=item.get('id', ''),
            title=DataUtils.clean_text(item.get('title', '')),
            published=DataUtils.extract_date(item.get('published', '')),
            source=item.get('source', ''),
            score=item.get('score'),
            href=item.get('href'),
            type=item.get('type', ''),
            language=item.get('language')
        )

    async def call_api(self, query: str = "Rce", max_pages: int = 100, step: int = 10) -> List[ExploitData]:
        self.logger.info(f"Starting API crawling for query: {query}")
        
        # Get cookies first
        self.cookies = await self._get_cookies_with_playwright(query)
        
        if not self.cookies:
            raise Exception("Failed to obtain cookies")
        
        all_exploits = []
        unique_ids = set()
        
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        
        with httpx.Client(http2=True, timeout=30, limits=limits) as client:
            for page_num in range(max_pages):
                offset = page_num * step
                
                try:
                    data = self.fetch_page(client, query, offset)
                    
                    # Handle different response structures
                    items = None
                    if isinstance(data, dict):
                        # Try common keys for the exploits array
                        for key in ("exploits", "items", "data", "results"):
                            if key in data and isinstance(data[key], list):
                                items = data[key]
                                break
                    
                    if not items:
                        self.logger.warning(f"No items found at offset {offset}, stopping pagination")
                        break
                    
                    new_exploits = 0
                    for item in items:
                        if isinstance(item, dict) and item.get('id'):
                            exploit_id = item.get('id')
                            if exploit_id not in unique_ids:
                                exploit = self.parse_exploit_data(item)
                                all_exploits.append(exploit)
                                unique_ids.add(exploit_id)
                                new_exploits += 1
                    
                    self.logger.info(f"Page {page_num + 1}: offset={offset}, new_exploits={new_exploits}, total={len(all_exploits)}")
                    
                    # If no new exploits, we might have reached the end
                    if new_exploits == 0:
                        self.logger.info("No new exploits found, stopping pagination")
                        break
                    
                    # Rate limiting between requests
                    time.sleep(Config.API_DELAY)
                    
                except Exception as e:
                    self.logger.error(f"Error fetching page {page_num + 1} at offset {offset}: {e}")
                    # Continue with next page on error
                    continue
        
        self.logger.info(f"API crawling completed: {len(all_exploits)} unique exploits found")
        return all_exploits
        
    async def run(self, query: str = "Rce", max_pages: int = 100) -> tuple[int, Path]:
        start_time = datetime.now()
        self.logger.info(f"Starting Sploitus crawler for query: {query}")
        
        try:
            # Crawl using API
            exploits = await self.call_api(query, max_pages)
            
            # Deduplicate
            exploits = DataUtils.deduplicate_exploits(exploits)
            
            self.logger.info(f"Found {len(exploits)} unique exploits after deduplication")
            
            # Save results
            json_file = await self._save_results(exploits, query)
            
            # Log completion
            end_time = datetime.now()
            duration = end_time - start_time
            self.logger.info(f"Crawling completed in {duration}")
            
            return len(exploits), json_file
            
        except Exception as e:
            self.logger.error(f"Critical error in crawler: {e}")
            raise

    async def _save_results(self, exploits: List[ExploitData], query: str) -> Path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f"sploitus_{query}_exploits_{timestamp}.json"
        json_file = FileUtils.save_exploits_json(exploits, json_filename)
        self.logger.info(f"Saved {len(exploits)} exploits to {json_file}")
        return json_file


async def main():
    try:
        crawler = SploitusCrawler()
        exploit_count, json_file = await crawler.run()
        
        print(f"\n{'='*60}")
        print(f"CRAWLING COMPLETED SUCCESSFULLY!")
        print(f"{'='*60}")
        print(f"Total unique exploits found: {exploit_count}")
        print(f"JSON file saved: {json_file}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"Crawler failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
