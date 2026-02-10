import json
import os
from datetime import datetime
import logging
from shared.config import config
from shared.utils import setup_logging

# Import ONLY financial news sources
from agent_watcher.sources.x_trends import fetch_x_trends
from agent_watcher.sources.rss import fetch_rss_trends

# Setup logging
logger = setup_logging(__name__)

def save_trends(data, x_trends=None, filename_prefix="trends"):
    """Saves the raw trend data to a daily file."""
    output_dir = config.DATA_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(output_dir, f"{filename_prefix}_{date_str}.json")

    final_data = {
        "topics": data,
        "x_hot_words": x_trends or []
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    logging.info(f"Saved {len(data)} topics and {len(x_trends or [])} X trends to {filepath}")

def load_source_config():
    config_path = os.path.join(os.path.dirname(__file__), "sources_config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def main():
    """
    Main execution flow to hunt FINANCIAL trends.
    Strictly filters out tech/programming content unless it's from a financial source.
    """
    logging.info("--- Financial Trend-Hunter Started (Maneko) ---")
    
    # 1. Load Sources Config
    sources = load_source_config()
    all_trends = []

    # Map only supported financial source types
    source_map = {
        "news_feed": fetch_rss_trends
        # Removed: github, product_hunt, zenn, qiita to prevent tech noise
    }

    for source in sources:
        sType = source.get("type")
        params = source.get("params", {})
        
        if sType in source_map:
            try:
                logging.info(f"Fetching from {sType}: {params.get('name', 'Unknown')}")
                
                # Fetch news with parameters (url, name)
                if sType == "news_feed":
                    trends = source_map[sType](url=params.get("url"), name=params.get("name"))
                else:
                    trends = []
                
                all_trends.extend(trends)
            except Exception as e:
                logging.error(f"Failed to fetch from {sType}: {e}")

    # Get X trends for viral context (Global context)
    x_hot_words = fetch_x_trends()
    
    # 2. Deduplication based on URL
    seen_urls = set()
    unique_trends = []
    for trend in all_trends:
        url = trend.get("url")
        if url and url not in seen_urls:
            unique_trends.append(trend)
            seen_urls.add(url)
            
    # 3. Sort by freshness (since news doesn't have stars)
    # Most RSS feeds return newest first, but let's ensure we keep order or shuffle if needed.
    # For now, we trust the source order.
    
    # 4. Save results
    save_trends(unique_trends, x_trends=x_hot_words)
    logging.info("--- Financial Trend-Hunter Completed ---")

if __name__ == "__main__":
    main()
