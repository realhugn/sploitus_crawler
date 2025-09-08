# Sploitus Exploit Crawler

A high-performance web crawler designed to extract security exploits from Sploitus.com using advanced API interception techniques. This tool combines browser automation with direct API calls to efficiently collect comprehensive exploit data while bypassing common web protections.

## 🚀 What This Tool Does

This crawler helps security researchers and professionals collect exploit information by:

- **API Interception**: Captures real-time data directly from Sploitus API responses
- **Intelligent Scrolling**: Automatically navigates through all available pages
- **Cloudflare Bypass**: Handles protection mechanisms without manual intervention  
- **Data Deduplication**: Removes duplicate entries using content hashing
- **Multi-format Output**: Saves results in both JSON and CSV formats
- **Performance Optimized**: Uses minimal system resources with smart rate limiting
- **Comprehensive Extraction**: Collects CVE numbers, CVSS scores, descriptions, and metadata
- **Modular Architecture**: Clean, maintainable codebase with separate concerns

## 📁 Project Structure

```
sploitus_crawler/
├── main.py              # Entry point with CLI argument parsing
├── crawler.py           # Core crawling logic and orchestration
├── api_handler.py       # API request handling and data processing
├── models.py            # Data structures and model definitions
├── config.py            # Configuration settings and constants
├── utils.py             # Utility functions and helpers
├── requirements.txt     # Python dependencies
├── CLI_USAGE.md        # Detailed command-line documentation
└── README.md           # This file

Generated during execution:
├── data/
│   ├── json/           # Structured exploit data (JSON)
│   ├── logs/           # Execution logs and debugging info
│   └── hashes/         # Duplicate detection storage
└── __pycache__/        # Python bytecode cache
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.7 or higher
- Internet connection
- ~100MB free disk space

### Step 1: Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Install browser automation tools
playwright install chromium
```

### Step 2: Quick Start
```bash
# Run with default settings (searches for RCE exploits)
python main.py

# Search for specific exploit types
python main.py -q "sql injection"
python main.py -q "privilege escalation"
```

## 🎯 Core Features

### Advanced API Interception
- Monitors network traffic to capture API responses
- Processes data directly from source endpoints
- Handles pagination automatically
- Maintains session integrity

### Smart Crawling Strategy
- **Hybrid Approach**: Browser setup + direct API calls
- **Rate Limiting**: Automatic delay adjustment based on server response
- **Error Recovery**: Continues operation despite partial failures
- **Progress Tracking**: Real-time status updates

### Data Quality Assurance
- **Hash-based Deduplication**: Prevents duplicate entries
- **Content Validation**: Ensures data integrity
- **Structured Output**: Consistent formatting across all results
- **Metadata Enrichment**: Extracts additional context information

## 🔧 Configuration Options

The [`Config`](config.py) class in [config.py](config.py) provides these customizable settings:

```python
# Search and crawling
BASE_URL = "https://sploitus.com/?query=Rce#exploits"
MAX_SCROLL_ATTEMPTS = 50
SCROLL_DELAY = 2.0

# Browser behavior  
HEADLESS_MODE = False
BROWSER_ARGS = [...]

# File management
DATA_DIR = Path("data")
JSON_DIR = DATA_DIR / "json"
LOGS_DIR = DATA_DIR / "logs"
HASH_FILE = DATA_DIR / "hashes" / "exploit_hashes.txt"
```

## 💻 Programming Interface

### Basic Usage
```python
from crawler import SploitusCrawler
import asyncio

async def collect_exploits():
    crawler = SploitusCrawler()
    exploit_count, json_file, csv_file = await crawler.run()
    print(f"Successfully collected {exploit_count} exploits")
    print(f"Data saved to: {json_file}")

# Run the crawler
asyncio.run(collect_exploits())
```

### Advanced Configuration
```python
# Customize before running
from config import Config

Config.HEADLESS_MODE = True
Config.MAX_SCROLL_ATTEMPTS = 100
Config.SCROLL_DELAY = 1.0

# Then run normally
crawler = SploitusCrawler()
results = await crawler.run()
```

## 📊 Output Data Structure

### JSON Format
Each exploit entry contains:
```json
{
  "id": "unique_identifier",
  "title": "Exploit Title",
  "published": "2024-01-15",
  "score": "9.8",
  "type": "Remote Code Execution",
  "verified": true,
  "cve": "CVE-2024-1234",
  "source": "detailed_content_and_metadata",
  "description": "exploit_description",
  "author": "researcher_name",
  "platform": "affected_systems"
}
```

### File Outputs
- **JSON**: `sploitus_{query}_exploits_YYYYMMDD_HHMMSS.json`
- **CSV**: `sploitus_{query}_exploits_YYYYMMDD_HHMMSS.csv`  
- **Logs**: `data/logs/sploitus_crawler.log`
- **Hashes**: `data/hashes/exploit_hashes.txt`

## 🔍 Command Line Interface

For detailed CLI usage, see [CLI_USAGE.md](CLI_USAGE.md).

### Key Commands
```bash
# Basic searches
python main.py -q "buffer overflow"
python main.py -q "xss" --headless

# Performance tuning
python main.py -q "rce" --max-steps 200 --api-delay 1.5

# Custom output
python main.py -q "code injection" --output-dir "custom_folder"

# Debug mode
python main.py -q "sql injection" --log-level DEBUG
```

## 🛠️ Technical Architecture

### Core Components

1. **[`main.py`](main.py)**: CLI interface and argument processing
2. **[`crawler.py`](crawler.py)**: Main orchestration and browser management
3. **[`api_handler.py`](api_handler.py)**: API interception and data processing
4. **[`models.py`](models.py)**: Data structures and validation
5. **[`config.py`](config.py)**: Configuration management
6. **[`utils.py`](utils.py)**: Utility functions and helpers

### Data Flow
1. Browser launches and navigates to target URL
2. API interceptor captures network responses
3. Data processor extracts and validates exploit information
4. Deduplication system prevents duplicate entries
5. Results exported to JSON and CSV formats

## 🔧 Troubleshooting

### Common Issues

**Browser Installation Error**
```bash
playwright install chromium
```

**Cloudflare Blocking**
- Set `HEADLESS_MODE = False` in [`config.py`](config.py)
- Check log files for detailed error information

**Low Result Count**
- Increase `MAX_SCROLL_ATTEMPTS` in [`config.py`](config.py)
- Verify network connectivity
- Check [`data/logs/sploitus_crawler.log`](data/logs/sploitus_crawler.log)

**Memory Issues**
- Reduce `MAX_SCROLL_ATTEMPTS` setting
- Close other applications during execution

### Debug Mode
```bash
python main.py -q "your_query" --log-level DEBUG
```

## 📋 Requirements

See [requirements.txt](requirements.txt) for complete dependency list:
- `playwright>=1.40.0` - Browser automation
- `aiohttp>=3.9.0` - Async HTTP client  
- `beautifulsoup4>=4.12.0` - HTML parsing
- `pandas>=2.0.0` - Data manipulation
- Additional utilities for data processing

## ⚖️ Legal & Ethical Use

This tool is designed for:
- **Security Research**: Authorized vulnerability assessment
- **Educational Purposes**: Learning about web scraping techniques
- **Professional Use**: Legitimate security testing

**Important**: Always respect website terms of service and implement appropriate rate limiting.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing code structure in [`models.py`](models.py) and [`config.py`](config.py)
4. Add appropriate error handling as shown in [`api_handler.py`](api_handler.py)
5. Update documentation accordingly

## 📄 License

This project is provided for educational and security research purposes. Please use responsibly and in accordance with applicable laws and terms of service.