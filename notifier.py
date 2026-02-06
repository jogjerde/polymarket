"""Notification module for sending alerts via Telegram."""

import requests
import logging
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications via Telegram bot."""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram notifier.
        
        Args:
            bot_token: Telegram bot token from @BotFather
            chat_id: Your Telegram chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message: str) -> bool:
        """
        Send a message via Telegram.
        
        Args:
            message: Message text to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not configured")
            return False
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Telegram notification sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False
    
    def send_top_markets(self, df: pd.DataFrame, top_n: int = 4) -> bool:
        """
        Send top N markets to Telegram.
        
        Args:
            df: DataFrame with market analysis results
            top_n: Number of top markets to send
            
        Returns:
            True if successful, False otherwise
        """
        if len(df) == 0:
            return self.send_message("⚠️ Ingen markets funnet i denne kjøringen.")
        
        # Take top N markets
        top_markets = df.head(top_n)
        
        # Build message
        message = f"🎯 <b>TOP {min(top_n, len(top_markets))} POLYMARKET BETS</b>\n\n"
        
        for idx, row in top_markets.iterrows():
            market_num = idx + 1
            title = row.get("Market Title", "Unknown")
            outcomes = row.get("Outcomes", "")
            wallets = row.get("Total Wallets", "")
            
            message += f"<b>{market_num}. {title}</b>\n"
            
            if "|" in str(outcomes):
                # Split outcomes into YES and NO sides
                parts = str(outcomes).split("|", 1)
                yes_side = parts[0].strip()
                no_side = parts[1].strip()
                message += f"   ✅ {yes_side}\n"
                message += f"   ❌ {no_side}\n"
            else:
                message += f"   📊 {outcomes}\n"
            
            message += f"   👥 {wallets} traders\n\n"
        
        return self.send_message(message)
