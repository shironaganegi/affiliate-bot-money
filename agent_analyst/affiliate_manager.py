
import json
import random
import os
from agent_analyst.product_recommender import search_related_items
from shared.config import config
from shared.utils import setup_logging

logger = setup_logging(__name__)

class AffiliateManager:
    def __init__(self):
        self.books_db = self._load_books_db()
        self.ads_db = self._load_ads_db()

    def _load_ads_db(self):
        """Loads custom affiliate ads (high ticket)"""
        db_path = os.path.join(config.DATA_DIR, "ads.json")
        try:
            if os.path.exists(db_path):
                with open(db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load ads DB: {e}")
        return []

    def _load_books_db(self):
        db_path = os.path.join(config.DATA_DIR, "technical_books.json")
        try:
            if os.path.exists(db_path):
                with open(db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load technical books DB: {e}")
        return {}

    def get_recommendations(self, article_text, keywords, limit=3):
        """
        Returns HTML string of recommended products.
        Priority:
        1. Technical Book matching specific keyword
        2. Rakuten Search for specific keyword
        3. Fallback to generic tech items
        """
        reccomendations = []
        html_output = ""

        # 0. Custom High-Ticket Ads (Priority #1)
        found_ad = self._search_custom_ads(article_text, keywords)
        if found_ad:
            logger.info(f"Found custom ad match: {found_ad['name']}")
            html_output += self._format_custom_ad(found_ad)
        
        # 1. Search for Tech/Investment Books (Priority #2)
        found_books = self._search_books(article_text, keywords)
        if found_books:
            logger.info(f"Found related books: {found_books}")
            for book_kw in found_books[:limit]:
                items = search_related_items(book_kw) # Use existing Rakuten search with book title
                if items:
                    html_output += "".join(items)
        
        # If we have enough recommendations, return
        if len(html_output) > 200: # Heuristic check if HTML is populated
             return self._wrap_output(html_output)

        # 2. Tech Keyword Search (Existing logic)
        for kw in keywords[:2]:
             items = search_related_items(kw)
             if items:
                 html_output += "".join(items)
        
        if len(html_output) > 200:
             return self._wrap_output(html_output)

        # 3. Fallback (Gadgets)
        fallback_items = ["ロジクール マウス", "Anker 充電器", "USB-C ケーブル"]
        for fb in fallback_items:
            items = search_related_items(fb)
            if items:
                html_output += "".join(items)
                break
        
        # 4. Emergency Link
        if not html_output:
            html_output = """
### 👇 エンジニアにおすすめのサービス 👇
[**🌐 独自ドメイン取得なら「お名前.com」。TechTrend Watchも使っています！**](https://www.onamae.com/)
"""
        return self._wrap_output(html_output)

    def _search_books(self, text, keywords):
        """Finds specific book titles based on keywords present in text."""
        candidates = []
        text_lower = text.lower()
        
        # Check against DB keys
        for category, books in self.books_db.items():
            # If category name (e.g. "Python") is in text or keywords
            if category.lower() in text_lower or any(category.lower() in k.lower() for k in keywords):
                for book in books:
                    candidates.append(book["keyword"])
        
        # Shuffle to avoid same book every time
        random.shuffle(candidates)
        random.shuffle(candidates)
        return candidates

    def _search_custom_ads(self, text, keywords):
        """Check if any custom ad keywords match the article context."""
        text_lower = text.lower()
        if not self.ads_db:
            return None
            
        # Shuffle ads to give equal chance if multiple match
        candidates = [ad for ad in self.ads_db if ad.get("active", True)]
        random.shuffle(candidates)

        for ad in candidates:
            # Check against ad specific keywords
            ad_keywords = ad.get("keywords", [])
            # Search in article text or provided keywords
            if any(k.lower() in text_lower for k in ad_keywords) or \
               any(any(k.lower() in kw.lower() for kw in keywords) for k in ad_keywords):
                
                # Check if URL is set (not placeholder)
                if "YOUR_AFFILIATE_LINK_HERE" not in ad.get("campaign_url", ""):
                    return ad
        return None

    def _format_custom_ad(self, ad):
        """Formats a custom ad as a prominent button or box."""
        url = ad.get("campaign_url", "#")
        text = ad.get("click_text", "詳細はこちら")
        desc = ad.get("description", "")
        
        return f"""
<div style="border: 2px solid #e5e7eb; padding: 20px; margin: 20px 0; border-radius: 8px; background-color: #f9fafb; text-align: center;">
    <p style="font-weight: bold; margin-bottom: 10px; color: #1f2937;">{desc}</p>
    <a href="{url}" target="_blank" rel="noopener noreferrer" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; transition: background-color 0.3s;">
        {text} 
    </a>
    <p style="font-size: 0.8em; color: #6b7280; margin-top: 5px;">(PR)</p>
</div>
"""

    def _wrap_output(self, html):
        return f"\n<!-- AFFILIATE_START -->\n{html}\n<!-- AFFILIATE_END -->\n"

# Singleton
affiliate_manager = AffiliateManager()
