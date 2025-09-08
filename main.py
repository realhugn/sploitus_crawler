import asyncio
import argparse
from pathlib import Path
from crawler import SploitusCrawler
from config import Config


def parse_args():
    parser = argparse.ArgumentParser(
        description="Sploitus Crawler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default RCE query (hybrid mode)
  python main.py

  # Custom query with API crawling
  python main.py -q "sql injection" --max-steps 50

  # Headless mode with custom API delay
  python main.py -q "xss" --headless --api-delay 2.0

  # Custom output directory and max pages
  python main.py -q "rce" --output-dir "my_results" --max-steps 200

  # Full customization for hybrid crawling
  python main.py -q "privilege escalation" --headless --max-steps 75 \\
                 --api-delay 1.5 --output-dir "priv_esc"
        """
    )
    
    # Query options
    parser.add_argument(
        '-q', '--query',
        type=str,
        default='Rce',
        help='Search query for exploits (default: Rce)'
    )
    
    # Crawler behavior
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (default: False)'
    )
    
    parser.add_argument(
        '--max-scrolls',
        type=int,
        default=50,
        help='Maximum number of scroll attempts (default: 50)'
    )
    
    parser.add_argument(
        '--scroll-delay',
        type=float,
        default=2.0,
        help='Delay between scrolls in seconds (default: 2.0)'
    )
    
    # Output options
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='Output directory for results (default: data)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    # Browser options
    parser.add_argument(
        '--user-agent',
        type=str,
        help='Custom user agent string'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=60,
        help='Page load timeout in seconds (default: 60)'
    )
    
    # Advanced options
    parser.add_argument(
        '--api-delay',
        type=float,
        default=1.0,
        help='Delay between direct API calls in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '--max-steps',
        type=int,
        default=100,
        help='Maximum number of steps to crawl via API (default: 100)'
    )
    
    return parser.parse_args()


def update_config_from_args(args):
    # Update URLs based on query
    query_encoded = args.query.replace(' ', '%20')
    Config.BASE_URL = f"https://sploitus.com/?query={query_encoded}#exploits"
    
    # Update crawler settings
    Config.HEADLESS_MODE = args.headless
    Config.MAX_SCROLL_ATTEMPTS = args.max_scrolls
    Config.SCROLL_DELAY = args.scroll_delay
    
    # Update file paths
    Config.DATA_DIR = Path(args.output_dir)
    Config.JSON_DIR = Config.DATA_DIR / "json"
    Config.LOGS_DIR = Config.DATA_DIR / "logs"
    Config.HASH_FILE = Config.DATA_DIR / "hashes" / "exploit_hashes.txt"
    Config.LOG_FILE = Config.LOGS_DIR / "sploitus_crawler.log"
    
    if args.user_agent:
        Config.BROWSER_ARGS = [arg for arg in Config.BROWSER_ARGS if not arg.startswith('--user-agent')]
        Config.BROWSER_ARGS.append(f'--user-agent={args.user_agent}')
    
    Config.API_DELAY = args.api_delay
    Config.LOG_LEVEL = args.log_level
    Config.PAGE_TIMEOUT = args.timeout * 1000


async def main():
    """Main CLI entry point."""
    args = parse_args()
    
    # Update configuration with CLI arguments
    update_config_from_args(args)
    
    print("Sploitus Crawler Starting...")
    print(f"Query: {args.query}")
    print(f"Headless Mode: {args.headless}")
    print(f"Max Pages: {args.max_pages}")
    print(f"API Delay: {args.api_delay}s")
    print(f"Output Directory: {args.output_dir}")
    print("-" * 50)
    
    try:
        crawler = SploitusCrawler()
        exploit_count, json_file = await crawler.run(query=args.query, max_pages=args.max_pages)
        
        print(f"\n{'='*60}")
        print(f"CRAWLING COMPLETED SUCCESSFULLY!")
        print(f"{'='*60}")
        print(f"Query: {args.query}")
        print(f"Total unique exploits found: {exploit_count}")
        print(f"JSON file saved: {json_file}")
        print(f"{'='*60}")
        
    except KeyboardInterrupt:
        print("\n❌ Crawling interrupted by user")
    except Exception as e:
        print(f"❌ Crawler failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
