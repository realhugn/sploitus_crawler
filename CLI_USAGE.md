# Command Line Usage Guide

## Getting Started Quickly

```bash
# Run with default settings
python main.py

# Search for SQL injection exploits
python main.py -q "sql injection"
```

## Options

### Search Options
- `-q, --query TEXT` - What type of exploits to search for (default: "Rce")

### Browser Settings  
- `--headless` - Hide the browser window while running (default: show browser)
- `--max-steps INT` - Max step to crawl (default: 100)
- `--api-delay FLOAT` - Delays in each api calls (default: 1.0)

### File and Folder Options
- `--output-dir TEXT` - Output directory (default: "data" folder)
- `--log-level TEXT` - DEBUG, INFO, WARNING, ERROR (default: INFO)

### Advanced Browser Options
- `--user-agent TEXT` - Pretend to be a different browser (optional)
- `--timeout INT` - How long to wait for pages to load in seconds (default: 60)

### Legacy Options (Not Used)
These options are kept for compatibility but don't affect the current version:
- `--max-scrolls INT` - No longer used
- `--scroll-delay FLOAT` - No longer used

## How This Crawler Works

This tool uses a smart two-step approach:

1. **Get Past Security**: First, it opens a real browser to get past Cloudflare and other protections
2. **Fast Data Collection**: Then it switches to making direct, fast requests to collect data
3. **Complete Coverage**: It automatically goes through all available pages
4. **Smart Rate Limiting**: It automatically slows down if the server gets overwhelmed

## Simple Examples

### Basic Searches
```bash
# Default search for RCE (Remote Code Execution) exploits
python main.py

# Look for SQL injection vulnerabilities  
python main.py -q "sql injection"

# Search for cross-site scripting (XSS) issues
python main.py -q "xss" --max-pages 200
```

### More Advanced Examples
```bash
# Run without showing browser window and check more pages
python main.py -q "privilege escalation" --headless --max-pages 150

# Save results to a custom folder with slower requests (gentler on server)
python main.py -q "buffer overflow" --output-dir "buffer_overflows" --api-delay 2.0

# Comprehensive search with custom settings
python main.py -q "code injection" \
               --headless \
               --max-pages 200 \
               --api-delay 1.5 \
               --output-dir "code_injection_results" \
               --timeout 120

# Turn on detailed logging to see what's happening
python main.py -q "rce" --log-level DEBUG

# Fast execution with minimal waiting
python main.py -q "xss" --api-delay 0.5 --max-pages 50
```

### Performance-Focused Examples
```bash
# Maximum speed (fast requests, hidden browser, many pages)
python main.py -q "rce" --headless --api-delay 0.5 --max-pages 300

# Maximum coverage (check lots of pages, but be gentle with server)
python main.py -q "rce" --max-pages 500 --api-delay 2.0

# Balanced approach (good speed and coverage)
python main.py -q "rce" --headless --max-pages 100 
```

## Why This Approach Works So Well

### Speed Benefits
- **10-50 times faster** than traditional browser automation
- **Multiple requests at once** when possible
- **No graphics rendering** after the initial setup phase

### Reliability Benefits
- **Automatic retry system** that gets smarter with each attempt
- **Handles rate limits** gracefully (when servers ask us to slow down)
- **Gets past Cloudflare** using the initial browser session
- **Complete page coverage** by checking all available pages systematically

### Data Quality Benefits
- **Gets everything available** by checking all pages methodically
- **Removes duplicates** automatically
- **Well-organized data** extracted directly from API responses
- **Keeps working** even when some requests fail

## What Files You'll Get

After running the crawler, you'll find these files in your output directory:

```
your-output-dir/
├── json/
│   └── sploitus_{your-search}_exploits_YYYYMMDD_HHMMSS.json
├── logs/
│   └── sploitus_crawler.log
└── hashes/
    └── exploit_hashes.txt
```

## Tips for Better Search Results

- **Be specific**: Use terms like "privilege escalation", "buffer overflow", or "sql injection"
- **Combine terms**: Try "remote code execution windows" or "linux kernel exploit"
- **Use CVE numbers**: Search for "CVE-2023" to find recent vulnerabilities
- **Target platforms**: Try "wordpress vulnerability" or "apache exploit"
- **Use application names**: Search for "nginx", "mysql", "windows", etc.

## Getting Better Performance

1. **For faster execution**: Use `--headless` to hide the browser and reduce `--api-delay`
2. **For more results**: Increase `--max-pages` to check more pages
3. **To be gentler on servers**: Increase `--api-delay` to 2.0 seconds or higher
4. **For troubleshooting**: Use `--log-level DEBUG` to see detailed information about what's happening

## Solving Common Problems

### Browser Issues
```bash
# If the browser crashes or takes too long to start
python main.py -q "rce" --timeout 180

# If you're getting blocked by rate limits
python main.py -q "rce" --api-delay 3.0

# If API responses seem empty or incomplete
python main.py -q "rce" --log-level DEBUG

# For debugging the initial browser setup
python main.py -q "rce" --log-level DEBUG
```

### Making Sure Everything is Set Up
Make sure you have installed all the required software:

```bash
pip install -r requirements.txt
playwright install chromium
```

If you get errors about missing packages, run these commands and try again.
