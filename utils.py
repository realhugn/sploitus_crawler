import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Set
from playwright.async_api import Page

from models import ExploitData
from config import Config


class FileUtils:
    @staticmethod
    def load_existing_hashes() -> Set[str]:
        hashes = set()
        if Config.HASH_FILE.exists():
            try:
                with open(Config.HASH_FILE, 'r', encoding='utf-8') as f:
                    hashes = set(line.strip() for line in f if line.strip())
            except Exception as e:
                logging.warning(f"Could not load existing hashes: {e}")
        return hashes
    
    @staticmethod
    def save_hashes(hashes: Set[str]):
        try:
            with open(Config.HASH_FILE, 'w', encoding='utf-8') as f:
                for hash_val in sorted(hashes):
                    f.write(f"{hash_val}\n")
        except Exception as e:
            logging.error(f"Could not save hashes: {e}")
    
    @staticmethod
    def save_exploits_json(exploits: List[ExploitData], filename: str) -> Path:
        filepath = Config.JSON_DIR / filename
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump([exploit.to_dict() for exploit in exploits], f, indent=2, ensure_ascii=False)
            return filepath
        except Exception as e:
            logging.error(f"Could not save JSON file: {e}")
            raise
    
class BrowserUtils:
    @staticmethod
    async def bypass_cloudflare(page: Page, logger: logging.Logger):
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=30000)
            
            # Check if we're on a Cloudflare challenge page
            if await page.locator('text=Checking your browser').count() > 0:
                logger.info("Cloudflare challenge detected, waiting...")
                await page.wait_for_load_state('networkidle', timeout=30000)
            
            # Additional wait for any redirects
            await asyncio.sleep(3)
            logger.info("Successfully bypassed Cloudflare protection")
            
        except Exception as e:
            logger.warning(f"Cloudflare bypass warning: {e}")


class DataUtils:
    @staticmethod
    def deduplicate_exploits(exploits: List[ExploitData]) -> List[ExploitData]:
        """Remove duplicate exploits based on title hash."""
        seen_hashes = set()
        unique_exploits = []
        
        for exploit in exploits:
            exploit_hash = exploit.get_hash()
            if exploit_hash not in seen_hashes:
                seen_hashes.add(exploit_hash)
                unique_exploits.append(exploit)
        
        return unique_exploits
    
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common HTML entities
        html_entities = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&hellip;': '...'
        }
        
        for entity, replacement in html_entities.items():
            text = text.replace(entity, replacement)
        
        return text.strip()
    
    @staticmethod
    def extract_date(date_str: str) -> str:
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Try parsing common formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    date_obj = datetime.strptime(date_str.strip(), fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return DataUtils.clean_text(date_str)
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')
