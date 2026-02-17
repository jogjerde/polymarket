"""Main analysis module for Polymarket trades."""

from typing import Dict, List, Any
import pandas as pd
import logging
from config import TRADER_RATINGS, SHOW_INDIVIDUAL_RATINGS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_outcome_with_individual_ratings(traders_detailed: Dict[str, Dict[str, Any]]) -> str:
    """
    Format outcome display with individual trader ratings and total size.
    
    Args:
        traders_detailed: {trader_name: {size, price, rating, count}}
        
    Returns:
        Formatted string like "OUTCOME: [3 7 5] $500 ($0.650)"
    """
    if not traders_detailed:
        return ""
    
    # Get all ratings as list (include unrated traders as '-')
    ratings = []
    total_size = 0
    prices = []
    
    for trader_name, info in traders_detailed.items():
        rating = info.get("rating")
        if isinstance(rating, int):
            ratings.append(str(rating))
        else:
            ratings.append("-")
        size = info.get("size", 0)
        total_size += size
        price = info.get("price", 0.5)
        prices.append(price)
    
    ratings_str = "[" + " ".join(ratings) + "]" if ratings else ""
    size_str = f"${total_size:.0f}" if total_size > 0 else ""
    
    # Calculate average entry price
    avg_price = sum(prices) / len(prices) if prices else 0.5
    price_str = f"(${avg_price:.3f})"
    
    parts = [ratings_str, size_str, price_str]
    return " ".join([p for p in parts if p])


class PolymarketAnalyzer:
    """Main analyzer class that orchestrates the analysis."""
    
    def __init__(self, api, processor):
        self.api = api
        self.processor = processor
    
    def analyze(self, wallets: List[str]) -> pd.DataFrame:
        """
        Perform complete analysis for given wallets.
        
        Args:
            wallets: List of wallet addresses to track
            
        Returns:
            DataFrame with analysis results
        """
        logger.info(f"Starting analysis for {len(wallets)} wallets")
        
        # Step 1: Fetch trades for all wallets
        wallet_trades = {}
        total_trades = 0
        all_trades_list = []
        
        for wallet in wallets:
            trades = self.api.fetch_trades(wallet)
            wallet_trades[wallet] = trades
            total_trades += len(trades)
            all_trades_list.extend(trades)
        
        logger.info(f"Fetched {total_trades} total trades from {len(wallets)} wallets")
        
        if total_trades == 0:
            logger.warning("No trades found for any wallet")
            return pd.DataFrame()
        
        # Filter to only top 600 most recent trades
        all_trades_sorted = sorted(all_trades_list, key=lambda x: x.get("timestamp", 0), reverse=True)
        recent_trades = all_trades_sorted[:600]
        
        if len(recent_trades) < len(all_trades_sorted):
            logger.info(f"Filtering to 600 most recent trades (out of {len(all_trades_sorted)} total)")
        
        # Reconstruct wallet_trades with only recent trades
        recent_condition_ids = set(t.get("conditionId") for t in recent_trades)
        wallet_trades_filtered = {}
        for wallet, trades in wallet_trades.items():
            wallet_trades_filtered[wallet] = [t for t in trades if t.get("conditionId") in recent_condition_ids]
        
        # Step 2: Process trades (extract markets, filter LIVE, group by market)
        market_data = self.processor.process(wallet_trades_filtered)
        trader_stats = self.processor.trader_stats
        
        # Step 3: Create trader summary with ratings
        trader_df = None
        if trader_stats:
            trader_results = []
            for trader_name, stats in sorted(trader_stats.items(), key=lambda x: x[1]["total_size"], reverse=True):
                rating = TRADER_RATINGS.get(trader_name, "-")
                trader_results.append({
                    "Trader": trader_name,
                    "Rating": rating,
                    "Bets": stats["trades"],
                    "Avg Entry Price": f"${stats['avg_price']:.3f}",
                    "Total Size": f"${stats['total_size']:.2f}",
                })
            trader_df = pd.DataFrame(trader_results)
            logger.info(f"Trader summary: {len(trader_df)} traders with bets >= $10")
        
        # Step 4: Convert markets to DataFrame
        results = []
        for condition_id, data in market_data.items():
            outcome_traders_detailed = data.get("outcome_traders_detailed", {})
            
            if not outcome_traders_detailed:
                continue  # Skip if no traders after filtering
            
            # Format outcomes based on SHOW_INDIVIDUAL_RATINGS setting
            if SHOW_INDIVIDUAL_RATINGS:
                # New format: [rating1 rating2 rating3] $total
                outcomes_list = []
                for outcome in sorted(outcome_traders_detailed.keys()):
                    traders_info = outcome_traders_detailed[outcome]
                    formatted = format_outcome_with_individual_ratings(traders_info)
                    outcomes_list.append(f"{outcome}: {formatted}")
                
                if len(outcomes_list) >= 2:
                    outcomes_display = f"{outcomes_list[0]} | {outcomes_list[1]}"
                else:
                    outcomes_display = outcomes_list[0] if outcomes_list else ""
            else:
                # Old format: with average rating
                outcomes_list = []
                for outcome in sorted(outcome_traders_detailed.keys()):
                    traders_info = outcome_traders_detailed[outcome]
                    count = len(traders_info)
                    
                    # Calculate average rating
                    ratings = [v.get("rating") for v in traders_info.values() if isinstance(v.get("rating"), int)]
                    avg_rating = sum(ratings) / len(ratings) if ratings else 0
                    
                    # Calculate total size
                    total_size = sum(v.get("size", 0) for v in traders_info.values())
                    
                    outcome_str = f"{outcome}: {count} (${total_size:.0f})"
                    if ratings:
                        outcome_str += f" MMR: {avg_rating:.1f}"
                    
                    outcomes_list.append(outcome_str)
                
                if len(outcomes_list) >= 2:
                    outcomes_display = f"{outcomes_list[0]} | {outcomes_list[1]}"
                else:
                    outcomes_display = outcomes_list[0] if outcomes_list else ""

            results.append({
                "Market Title": data["market_title"],
                "Market ID": data["market_id"],
                "Outcomes": outcomes_display,
                "Total Wallets": data["total_wallets"],
                "Latest Trade": data.get("latest_timestamp", 0),
            })

        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Sort by most recent trade timestamp (descending) to show newest trades first
        if len(df) > 0:
            df = df.sort_values("Latest Trade", ascending=False).reset_index(drop=True)

        logger.info(f"Analysis complete. Found {len(df)} markets to display")
        return df

    def export_csv(self, df: pd.DataFrame, filename: str):
        """
        Export results to CSV.

        Args:
            df: DataFrame to export
            filename: Output CSV filename
        """
        if len(df) == 0:
            logger.warning("No data to export")
            return

        df.to_csv(filename, index=False)
        logger.info(f"Results exported to {filename}")
