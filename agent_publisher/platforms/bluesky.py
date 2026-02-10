from atproto import Client, client_utils
from shared.config import config
from shared.utils import setup_logging

logger = setup_logging(__name__)

class BlueSkyPublisher:
    def __init__(self):
        self.handle = config.BLUESKY_HANDLE
        self.password = config.BLUESKY_PASSWORD

    def publish(self, title, zenn_url):
        if not self.handle or not self.password:
            logger.warning("BlueSky credentials missing. Skipping.")
            return

        try:
            client = Client()
            client.login(self.handle, self.password)
            
            # Use TextBuilder to create rich text with facets (links, hashtags)
            tb = client_utils.TextBuilder()
            
            # "📝 新しい記事を書きました！" (plain text)
            tb.text("📝 新しい記事を書きました！\n\n")
            
            # Title (plain text)
            tb.text(f"{title}\n\n")
            
            # Hashtags
            tb.tag("#AI", "AI").text(" ")
            tb.tag("#Tech", "Tech").text(" ")
            tb.tag("#Zenn", "Zenn").text("\n\n")
            
            # Link to the article
            # Using the title or "記事を読む" as the link text, linking to zenn_url
            tb.link("👉 記事を読む", zenn_url)
            
            client.send_post(tb)
            logger.info("Successfully posted to BlueSky!")
        except Exception as e:
            logger.error(f"BlueSky Error: {e}")
