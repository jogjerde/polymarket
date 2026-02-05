"""API module for fetching Polymarket data."""

import requests
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PolymarketAPI:
    """Handles API calls to Polymarket."""
    
    def __init__(self, base_url: str = "https://data-api.polymarket.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10
    
    def fetch_trades(self, wallet_address: str) -> List[Dict[str, Any]]:
        """
        Fetch all trades for a specific wallet.
        
        Args:
            wallet_address: Ethereum wallet address
            
        Returns:
            List of trade dictionaries
        """
        try:
            url = f"{self.base_url}/trades"
            params = {"user": wallet_address}
            
            logger.info(f"Fetching trades for wallet: {wallet_address}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            trades = response.json()
            logger.info(f"Retrieved {len(trades)} trades for {wallet_address}")
            return trades
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching trades for {wallet_address}: {e}")
            return []
    
    def fetch_market_metadata(self, condition_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetch market metadata by querying the markets endpoint.
        Note: The trades API already includes market metadata, so this is a fallback.
        
        Args:
            condition_ids: List of market condition IDs
            
        Returns:
            Dictionary mapping condition_id to market metadata
        """
        # Markets endpoint doesn't work well with large batch queries
        # We'll use market info from trades instead
        return {}
    
    def fetch_current_market_price(self, condition_id: str) -> Dict[str, float]:
        """
        Fetch current market prices by getting recent trades for a market.
        
        Args:
            condition_id: Market condition ID
            
        Returns:
            Dict with outcome prices, e.g. {outcome: price}
        """
        try:
            # Fetch recent trades for this specific market to get current prices
            # We'll use the trades data to infer current prices
            url = f"{self.base_url}/trades"
            params = {"condition_id": condition_id, "limit": 100}  # Get recent trades
            
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            trades = response.json()
            if trades and len(trades) > 0:
                # Group by outcome and get the most recent price for each
                outcome_prices = {}
                for trade in trades:
                    outcome = trade.get("outcome", "")
                    price = trade.get("price", 0.5)
                    
                    # Use the most recent (first) trade price for each outcome
                    if outcome not in outcome_prices:
                        outcome_prices[outcome] = float(price)
                
                return outcome_prices
            
            return {}
        
        except Exception as e:
            logger.debug(f"Error fetching current price for {condition_id}: {e}")
            return {}
    
    def close(self):
        """Close the session."""
        self.session.close()
