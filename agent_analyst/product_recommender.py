import os
import json
import random
import logging
from shared.config import config

logger = logging.getLogger(__name__)

def load_ads():
    try:
        with open(config.ADS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load ads from {config.ADS_FILE}: {e}")
        return []

def search_related_items(keywords):
    """
    Selects the best financial affiliate offer based on keywords.
    Instead of searching for random goods (t-shirts, mugs) on Rakuten,
    we prioritize high-ticket financial services (Exchanges, NISA).
    """
    if isinstance(keywords, str):
        keywords = [keywords]
    
    ads = load_ads()
    if not ads:
        return ""

    # Normalize keywords for matching
    keywords_lower = [k.lower() for k in keywords]
    
    matched_ad = None
    
    # 1. Try to find a matching ad based on keywords
    # e.g. if keyword is "Bitcoin", show Coincheck or bitFlyer
    for ad in ads:
        ad_keywords = [k.lower() for k in ad.get('keywords', [])]
        # Check if any article keyword matches any ad keyword
        if any(ak in ' '.join(keywords_lower) for ak in ad_keywords):
            matched_ad = ad
            break
    
    # 2. Fallback: If no match, pick a random active ad (General Appeal)
    if not matched_ad:
        active_ads = [ad for ad in ads if ad.get('active', True)]
        if active_ads:
            matched_ad = random.choice(active_ads)
            
    if not matched_ad:
        return ""

    # Generate HTML/Markdown for the ad
    campaign_url = matched_ad.get('campaign_url', '#')
    click_text = matched_ad.get('click_text', '詳細はこちら')
    description = matched_ad.get('description', '')
    
    # Professional Call-to-Action Card for Zenn/Blog
    ad_html = f"""
:::message alert
**💰 【PR】資産形成の第一歩**

**{click_text}**

{description}

👉 [公式サイトでキャンペーンを確認する]({campaign_url})
:::
"""
    return ad_html

# Legacy functions kept for interface compatibility but redirected
def _search_rakuten(keyword):
    return []

def _search_amazon(keyword):
    return []
