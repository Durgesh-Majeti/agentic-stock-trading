"""Validate RSS feed URLs and check if they're accessible and well-formed."""
import sys
import feedparser
import requests
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.news_sources import get_all_active_sources, NewsSourceConfig
from loguru import logger


def validate_rss_url(url: str, source_name: str, timeout: int = 10) -> Tuple[bool, str, int]:
    """Validate an RSS feed URL.
    
    Returns:
        (is_valid, error_message, article_count)
    """
    try:
        # Try to fetch the feed
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Parse the feed
        feed = feedparser.parse(response.content)
        
        # Check for parsing errors
        if feed.bozo and feed.bozo_exception:
            return False, f"RSS parsing error: {feed.bozo_exception}", 0
        
        # Check if feed has entries
        article_count = len(feed.entries)
        if article_count == 0:
            return False, "Feed has no entries", 0
        
        return True, "OK", article_count
        
    except requests.exceptions.RequestException as e:
        return False, f"HTTP error: {str(e)}", 0
    except Exception as e:
        return False, f"Error: {str(e)}", 0


def validate_api_url(url: str, source_name: str, timeout: int = 10) -> Tuple[bool, str]:
    """Validate an API endpoint.
    
    Returns:
        (is_valid, error_message)
    """
    try:
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
        
        # Check if response is JSON
        try:
            data = response.json()
            return True, f"OK (JSON response, status: {response.status_code})"
        except ValueError:
            return False, f"Response is not valid JSON (status: {response.status_code})"
            
    except requests.exceptions.RequestException as e:
        return False, f"HTTP error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Validate all RSS feed URLs."""
    logger.info("=" * 70)
    logger.info("RSS Feed URL Validation")
    logger.info("=" * 70)
    
    sources = get_all_active_sources()
    
    results = {
        'valid': [],
        'invalid': [],
        'api': []
    }
    
    for source in sources:
        logger.info(f"\nValidating: {source.name}")
        logger.info(f"  URL: {source.url}")
        logger.info(f"  Type: {source.type}")
        
        if source.type == "rss":
            is_valid, error_msg, article_count = validate_rss_url(source.url, source.name)
            
            if is_valid:
                logger.info(f"  ✅ VALID - {article_count} articles found")
                results['valid'].append({
                    'name': source.name,
                    'url': source.url,
                    'article_count': article_count
                })
            else:
                logger.warning(f"  ❌ INVALID - {error_msg}")
                results['invalid'].append({
                    'name': source.name,
                    'url': source.url,
                    'error': error_msg
                })
        
        elif source.type == "api":
            is_valid, error_msg = validate_api_url(source.url, source.name)
            
            if is_valid:
                logger.info(f"  ✅ VALID - {error_msg}")
                results['api'].append({
                    'name': source.name,
                    'url': source.url,
                    'status': error_msg
                })
            else:
                logger.warning(f"  ❌ INVALID - {error_msg}")
                results['invalid'].append({
                    'name': source.name,
                    'url': source.url,
                    'error': error_msg
                })
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("Summary")
    logger.info("=" * 70)
    logger.info(f"✅ Valid RSS feeds: {len(results['valid'])}")
    logger.info(f"✅ Valid API endpoints: {len(results['api'])}")
    logger.info(f"❌ Invalid sources: {len(results['invalid'])}")
    
    if results['valid']:
        logger.info("\nValid RSS Feeds:")
        for item in results['valid']:
            logger.info(f"  - {item['name']}: {item['article_count']} articles")
    
    if results['api']:
        logger.info("\nValid API Endpoints:")
        for item in results['api']:
            logger.info(f"  - {item['name']}: {item['status']}")
    
    if results['invalid']:
        logger.warning("\nInvalid Sources (need fixing):")
        for item in results['invalid']:
            logger.warning(f"  - {item['name']}")
            logger.warning(f"    URL: {item['url']}")
            logger.warning(f"    Error: {item['error']}")
    
    logger.info("\n" + "=" * 70)
    
    return 0 if len(results['invalid']) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
