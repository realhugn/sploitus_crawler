from pathlib import Path

class Config:
    # URLs
    BASE_URL = "https://sploitus.com/?query=Rce#exploits" # Default search for RCE exploits
    SEARCH_API_URL = "https://sploitus.com/search"
    
    # File paths
    DATA_DIR = Path("data")
    JSON_DIR = DATA_DIR / "json"
    LOGS_DIR = DATA_DIR / "logs"
    HASH_FILE = DATA_DIR / "hashes" / "exploit_hashes.txt"
    LOG_FILE = LOGS_DIR / "sploitus_crawler.log"
    
    # Crawler settings
    HEADLESS_MODE = False
    MAX_SCROLL_ATTEMPTS = 50
    SCROLL_DELAY = 2.0  # seconds between scrolls
    SEARCH_API_PATH = "/search"
    
    # Browser settings
    BROWSER_ARGS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',
        '--disable-extensions',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    ]
    
    SKIP_API_CALLS = False
    API_DELAY = 1.0
    LOG_LEVEL = 'INFO'
    PAGE_TIMEOUT = 60000 #milliseconds
    
    @classmethod
    def create_directories(cls):
        for directory in [cls.DATA_DIR, cls.JSON_DIR, cls.LOGS_DIR, cls.HASH_FILE.parent]:
            directory.mkdir(parents=True, exist_ok=True)
