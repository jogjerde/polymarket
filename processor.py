"""Data processing module for Polymarket analysis."""

from typing import Dict, List, Any
from collections import defaultdict
import logging
import requests
import time
import re
from config import (
    CHECK_LIVE_STATUS,
    ONLY_SHOW_MARKET_KEYWORDS,
    MAX_MARKET_AGE_HOURS,
    CHECK_EXTERNAL_RESULTS,
    TRADER_RATINGS,
    MIN_BET_SIZE_PER_TRADER,
    ENABLE_VOLATILITY_FILTER,
    MAX_OUTCOME_PRICE_SPREAD,
    MIN_PRICES_FOR_VOLATILITY_CHECK,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradeProcessor:
    """Processes trade data and aggregates by market."""
    
    def __init__(self, min_wallets: int = 2):
        self.min_wallets = min_wallets
    
    def extract_market_info_from_trades(
        self,
        trades: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract unique market info from trades.
        Each trade contains: conditionId, title, slug, resolved, closed, etc.
        
        Args:
            trades: List of trade dictionaries
            
        Returns:
            Dict mapping condition_id to market metadata
        """
        markets = {}
        for trade in trades:
            condition_id = trade.get("conditionId")
            if condition_id and condition_id not in markets:
                markets[condition_id] = {
                    "condition_id": condition_id,
                    "title": trade.get("title", "Unknown Market"),
                    "slug": trade.get("slug", ""),
                    "resolved": trade.get("resolved", False),
                    "closed": trade.get("closed", False),
                }
        return markets
    
    def group_trades_by_market(
        self,
        wallet_trades: Dict[str, List[Dict[str, Any]]],
        live_markets: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Group trades by market and count YES/NO votes per wallet.
        
        Args:
            wallet_trades: Dict mapping wallet address to its trades
            live_markets: Dict mapping condition_id to market metadata
            
        Returns:
            Dict with market data including YES/NO counts and wallets involved
        """
        market_data = defaultdict(lambda: {
            "market_title": "",
            "market_id": "",
            "slug": "",
            "yes_wallets": [],
            "no_wallets": [],
            "wallet_outcomes": {},
            "yes_count": 0,
            "no_count": 0,
            "outcome_votes": {},  # Track actual outcomes and their vote counts
            "outcome_prices": {},  # Track prices separately per outcome
            "outcome_traders": {},  # Track trader names per outcome
            "outcome_traders_detailed": {},  # Track {outcome: {trader_name: {size, price, rating}}}
            "latest_timestamp": 0,  # Track most recent trade timestamp for sorting
            "prices": [],  # Track all entry prices for computing average
            "current_prices": {},  # Current market prices (will be fetched later)
        })
        
        for wallet, trades in wallet_trades.items():
            for trade in trades:
                condition_id = trade.get("conditionId")
                
                # Skip if not in live markets
                if condition_id not in live_markets:
                    continue
                
                market = live_markets[condition_id]
                outcome = trade.get("outcome", "").upper()
                if wallet not in market_data[condition_id]["wallet_outcomes"]:
                    market_data[condition_id]["wallet_outcomes"][wallet] = set()
                market_data[condition_id]["wallet_outcomes"][wallet].add(outcome)
                
                # Update market data
                if condition_id not in market_data or not market_data[condition_id]["market_title"]:
                    market_data[condition_id]["market_title"] = market.get("title", "N/A")
                    market_data[condition_id]["market_id"] = condition_id
                    market_data[condition_id]["slug"] = market.get("slug", "")
                
                # Track most recent trade timestamp for this market
                trade_ts = trade.get("timestamp", 0)
                if trade_ts > market_data[condition_id]["latest_timestamp"]:
                    market_data[condition_id]["latest_timestamp"] = trade_ts
                
                # Collect entry price
                price = trade.get("price", 0)
                if price:
                    market_data[condition_id]["prices"].append(price)
                    # Also track price per outcome
                    if outcome not in market_data[condition_id]["outcome_prices"]:
                        market_data[condition_id]["outcome_prices"][outcome] = []
                    market_data[condition_id]["outcome_prices"][outcome].append(price)
                
                # Count votes (outcome can be Yes/No or team name for sports/esports)
                # For binary markets: YES/NO
                # For multi-outcome: team name or outcome text
                if outcome in ["YES", "YES "]:
                    if wallet not in market_data[condition_id]["yes_wallets"]:
                        market_data[condition_id]["yes_wallets"].append(wallet)
                        market_data[condition_id]["yes_count"] += 1
                elif outcome in ["NO", "NO "]:
                    if wallet not in market_data[condition_id]["no_wallets"]:
                        market_data[condition_id]["no_wallets"].append(wallet)
                        market_data[condition_id]["no_count"] += 1
                else:
                    # For non-binary outcomes (team names, etc), count as YES vote
                    if wallet not in market_data[condition_id]["yes_wallets"]:
                        market_data[condition_id]["yes_wallets"].append(wallet)
                        market_data[condition_id]["yes_count"] += 1
                    
                    # Track the actual outcome
                    if outcome not in market_data[condition_id]["outcome_votes"]:
                        market_data[condition_id]["outcome_votes"][outcome] = 0
                    market_data[condition_id]["outcome_votes"][outcome] += 1
                    
                    # Track trader name per outcome
                    trader_name = trade.get("name") or trade.get("pseudonym") or wallet[:8]
                    if outcome not in market_data[condition_id]["outcome_traders"]:
                        market_data[condition_id]["outcome_traders"][outcome] = []
                    if trader_name not in market_data[condition_id]["outcome_traders"][outcome]:
                        market_data[condition_id]["outcome_traders"][outcome].append(trader_name)
                    
                    # Track detailed trader info (size, price, rating)
                    if outcome not in market_data[condition_id]["outcome_traders_detailed"]:
                        market_data[condition_id]["outcome_traders_detailed"][outcome] = {}
                    
                    trader_size = trade.get("size", 0)
                    trader_price = trade.get("price", 0.5)
                    trader_rating = TRADER_RATINGS.get(trader_name, "-")
                    trader_side = trade.get("side", "BUY")  # BUY or SELL
                    
                    if trader_name not in market_data[condition_id]["outcome_traders_detailed"][outcome]:
                        market_data[condition_id]["outcome_traders_detailed"][outcome][trader_name] = {
                            "size": 0,
                            "price": 0,
                            "rating": trader_rating,
                            "count": 0,
                            "sides": []  # Track BUY/SELL
                        }
                    
                    market_data[condition_id]["outcome_traders_detailed"][outcome][trader_name]["size"] += trader_size
                    market_data[condition_id]["outcome_traders_detailed"][outcome][trader_name]["price"] = trader_price
                    market_data[condition_id]["outcome_traders_detailed"][outcome][trader_name]["count"] += 1
                    market_data[condition_id]["outcome_traders_detailed"][outcome][trader_name]["sides"].append(trader_side)
        
        return market_data
    
    def filter_traders_on_both_sides(
        self,
        market_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Remove traders who betted on BOTH outcomes in the same market.
        These traders are either hedging/arbitraging, so they don't provide signal.
        
        Args:
            market_data: Market data dictionary
            
        Returns:
            Filtered market data
        """
        filtered = {}
        for market_id, data in market_data.items():
            filtered_data = data.copy()
            
            if "outcome_traders_detailed" not in filtered_data:
                filtered[market_id] = filtered_data
                continue
            
            # Collect all trader names across all outcomes
            traders_by_outcome = filtered_data["outcome_traders_detailed"]
            
            # Find traders who appear in multiple outcomes
            trader_appearances = {}
            for outcome, traders_dict in traders_by_outcome.items():
                for trader_name in traders_dict.keys():
                    if trader_name not in trader_appearances:
                        trader_appearances[trader_name] = []
                    trader_appearances[trader_name].append(outcome)
            
            # Identify traders on both sides
            traders_on_both_sides = {
                trader for trader, outcomes in trader_appearances.items() 
                if len(outcomes) > 1
            }
            
            # Remove these traders from all outcomes
            if traders_on_both_sides:
                new_traders_detailed = {}
                for outcome, traders_dict in traders_by_outcome.items():
                    new_traders_dict = {
                        name: info for name, info in traders_dict.items()
                        if name not in traders_on_both_sides
                    }
                    if new_traders_dict:
                        new_traders_detailed[outcome] = new_traders_dict
                
                filtered_data["outcome_traders_detailed"] = new_traders_detailed
            
            # Only keep market if it still has outcomes after filtering
            if filtered_data.get("outcome_traders_detailed"):
                filtered[market_id] = filtered_data
        
        return filtered
    
    def filter_traders_with_exits(
        self,
        market_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Remove traders who have both BUY and SELL on the same outcome.
        These traders have closed/exited their position.
        
        Args:
            market_data: Market data dictionary
            
        Returns:
            Filtered market data
        """
        filtered = {}
        for market_id, data in market_data.items():
            filtered_data = data.copy()
            
            if "outcome_traders_detailed" not in filtered_data:
                filtered[market_id] = filtered_data
                continue
            
            traders_by_outcome = filtered_data["outcome_traders_detailed"]
            new_traders_detailed = {}
            
            for outcome, traders_dict in traders_by_outcome.items():
                new_traders_dict = {}
                
                for trader_name, trader_info in traders_dict.items():
                    sides = trader_info.get("sides", [])
                    
                    # Check if trader has both BUY and SELL
                    has_buy = "BUY" in sides
                    has_sell = "SELL" in sides
                    
                    # Keep only if they haven't exited (either only BUY or only SELL)
                    if not (has_buy and has_sell):
                        new_traders_dict[trader_name] = trader_info
                
                if new_traders_dict:
                    new_traders_detailed[outcome] = new_traders_dict
            
            filtered_data["outcome_traders_detailed"] = new_traders_detailed
            
            # Only keep market if it still has outcomes after filtering
            if filtered_data.get("outcome_traders_detailed"):
                filtered[market_id] = filtered_data
        
        return filtered
    
    def filter_by_minimum_bet_size(
        self,
        market_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Filter out individual trader entries that are below their minimum bet size threshold.
        Keeps bets that are below threshold if they have very low probability (under 10%).
        
        Args:
            market_data: Market data dictionary
            
        Returns:
            Filtered market data
        """
        filtered = {}
        for market_id, data in market_data.items():
            filtered_data = data.copy()
            
            # Filter outcome_traders_detailed
            if "outcome_traders_detailed" in filtered_data:
                new_traders_detailed = {}
                for outcome, traders_dict in filtered_data["outcome_traders_detailed"].items():
                    new_traders_dict = {}
                    for trader_name, trader_info in traders_dict.items():
                        size = trader_info.get("size", 0)
                        min_size = MIN_BET_SIZE_PER_TRADER.get(trader_name, 0)
                        
                        # Calculate probability (using entry price as proxy)
                        price = trader_info.get("price", 0.5)
                        
                        # Include if: size >= min_size OR probability is very low (< 10% or > 90%)
                        if size >= min_size or price < 0.1 or price > 0.9:
                            new_traders_dict[trader_name] = trader_info
                    
                    if new_traders_dict:  # Only add outcome if it has traders left
                        new_traders_detailed[outcome] = new_traders_dict
                
                filtered_data["outcome_traders_detailed"] = new_traders_detailed
            
            # Only keep market if it still has outcomes after filtering
            if filtered_data.get("outcome_traders_detailed"):
                filtered[market_id] = filtered_data
        
        return filtered

    def filter_by_outcome_price_volatility(
        self,
        market_data: Dict[str, Dict[str, Any]],
        max_spread: float,
        min_prices: int,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Remove markets where at least one outcome has a large entry-price spread.

        This catches fast-moving / highly volatile markets where traders entered
        at very different prices in a short window.
        """
        filtered = {}
        for market_id, data in market_data.items():
            outcome_traders = data.get("outcome_traders_detailed", {})
            is_volatile = False

            for _, traders_dict in outcome_traders.items():
                prices = [
                    info.get("price")
                    for info in traders_dict.values()
                    if isinstance(info.get("price"), (int, float))
                ]

                if len(prices) < min_prices:
                    continue

                spread = max(prices) - min(prices)
                if spread > max_spread:
                    is_volatile = True
                    break

            if not is_volatile:
                filtered[market_id] = data

        return filtered
    
    def filter_by_minimum_wallets(
        self,
        market_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Filter markets to only include those with >= min_wallets involved.
        
        Args:
            market_data: Market data dictionary
            
        Returns:
            Filtered market data
        """
        filtered = {}
        for market_id, data in market_data.items():
            if data.get("wallet_outcomes"):
                total_wallets = len(data["wallet_outcomes"].keys())
            else:
                total_wallets = len(set(data["yes_wallets"] + data["no_wallets"]))
            if total_wallets >= self.min_wallets:
                data["total_wallets"] = total_wallets
                filtered[market_id] = data
        
        return filtered
    
    def filter_by_minimum_trader_difference(
        self,
        market_data: Dict[str, Dict[str, Any]],
        min_difference: int = 2
    ) -> Dict[str, Dict[str, Any]]:
        """
        Filter markets to only show those where one side has at least min_difference 
        more traders than the other side (e.g., 2-0, 3-1, 4-2, but not 2-1).
        
        Args:
            market_data: Market data dictionary
            min_difference: Minimum difference in trader count between sides
            
        Returns:
            Filtered market data
        """
        filtered = {}
        for market_id, data in market_data.items():
            if "outcome_traders_detailed" not in data:
                continue
            
            traders_by_outcome = data["outcome_traders_detailed"]
            
            # Count traders per outcome
            trader_counts = []
            for outcome, traders_dict in traders_by_outcome.items():
                trader_counts.append(len(traders_dict))
            
            # Need at least one outcome with traders
            if not trader_counts:
                continue
            
            # Calculate difference between highest and lowest count
            if len(trader_counts) == 1:
                # Only one outcome: difference is the count itself (vs 0)
                difference = trader_counts[0]
            else:
                # Multiple outcomes: difference between max and min
                difference = max(trader_counts) - min(trader_counts)
            
            # Keep market if difference meets minimum requirement
            if difference >= min_difference:
                filtered[market_id] = data
            else:
                logger.debug(f"Filtered {market_id}: trader difference {difference} < {min_difference}")
        
        return filtered

    def filter_markets_with_wallet_hedging(
        self,
        market_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Remove markets where any wallet has traded on multiple outcomes.
        """
        filtered = {}
        for market_id, data in market_data.items():
            wallet_outcomes = data.get("wallet_outcomes", {})
            has_hedger = any(len(outcomes) > 1 for outcomes in wallet_outcomes.values())
            if not has_hedger:
                filtered[market_id] = data
        return filtered

    def filter_by_majority_vote(
        self,
        market_data: Dict[str, Dict[str, Any]],
        threshold: float = 0.65
    ) -> Dict[str, Dict[str, Any]]:
        """
        Keep only markets where one outcome has at least threshold% of votes.
        Hedgers (wallets on multiple outcomes) count as negative votes for the majority.
        """
        filtered = {}
        for market_id, data in market_data.items():
            wallet_outcomes = data.get("wallet_outcomes", {})
            outcome_traders = data.get("outcome_traders_detailed", {})
            
            if not outcome_traders or not wallet_outcomes:
                continue
            
            # Count traders per outcome
            outcome_counts = {}
            for outcome, traders_dict in outcome_traders.items():
                outcome_counts[outcome] = len(traders_dict)
            
            # Count hedgers (wallets with multiple outcomes)
            hedgers = sum(1 for outcomes in wallet_outcomes.values() if len(outcomes) > 1)
            
            # Total votes = all wallets
            total_votes = len(wallet_outcomes)
            
            if total_votes == 0:
                continue
            
            # Find outcome with most votes
            max_outcome = max(outcome_counts.items(), key=lambda x: x[1])
            max_votes = max_outcome[1]
            
            # Calculate majority percentage
            # Hedgers effectively reduce the majority's strength
            majority_pct = max_votes / total_votes
            
            # Keep market if majority exceeds threshold
            if majority_pct >= threshold:
                filtered[market_id] = data
                logger.debug(f"✓ {market_id}: {max_votes}/{total_votes} ({majority_pct:.1%}) with {hedgers} hedgers")
            else:
                logger.debug(f"✗ {market_id}: {max_votes}/{total_votes} ({majority_pct:.1%}) below {threshold:.0%}")
        
        return filtered
    
    def get_market_live_status(self, slug: str) -> Dict[str, bool]:
        """
        Fetch current market status (resolved/closed) from polymarket.com page.
        
        Args:
            slug: Market URL slug
            
        Returns:
            Dict with 'resolved' and 'closed' booleans
        """
        if not slug:
            return {"resolved": False, "closed": False}
        
        url = f"https://polymarket.com/market/{slug}"
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            resp = requests.get(url, headers=headers, timeout=5)
            
            if resp.status_code != 200:
                # Page doesn't exist = market removed/archived
                return {"resolved": True, "closed": True}
            
            text = resp.text
            
            # Extract resolved and closed status from HTML
            resolved = False
            closed = False
            
            resolved_match = re.search(r'"resolved"\s*:\s*(true|false)', text, re.IGNORECASE)
            if resolved_match:
                resolved = resolved_match.group(1).lower() == 'true'
            
            closed_match = re.search(r'"closed"\s*:\s*(true|false)', text, re.IGNORECASE)
            if closed_match:
                closed = closed_match.group(1).lower() == 'true'
            
            return {"resolved": resolved, "closed": closed}
        
        except Exception as e:
            logger.debug(f"Error fetching market status for {slug}: {e}")
            # On error, assume market is not live
            return {"resolved": True, "closed": True}
    
    def check_external_result(self, title: str) -> bool:
        """
        Check external sources to see if this market/event is already finished.
        Returns True if the market appears to be finished based on external data.
        
        Args:
            title: Market title to check
            
        Returns:
            True if market appears finished, False otherwise
        """
        if not CHECK_EXTERNAL_RESULTS:
            return False
            
        try:
            title_lower = title.lower()
            
            # Check if it's a past date event
            # Look for dates in format like "2026-02-03", "2026-02-04"
            date_pattern = r'202[0-9]-\d{2}-\d{2}'
            date_match = re.search(date_pattern, title)
            if date_match:
                event_date_str = date_match.group(0)
                try:
                    from datetime import datetime, timezone
                    event_date = datetime.strptime(event_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                    current_date = datetime.now(timezone.utc)
                    
                    # If event date is more than 1 day in the past, mark as finished
                    days_ago = (current_date - event_date).days
                    if days_ago > 1:
                        logger.debug(f"Event from {days_ago} days ago, marking as finished: {title}")
                        return True
                except:
                    pass
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking external result for {title}: {e}")
            return False
    
    def process(
        self,
        wallet_trades: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Full processing pipeline.
        
        Args:
            wallet_trades: Dict mapping wallet address to its trades
            
        Returns:
            Processed and filtered market data
        """
        # Extract all markets from trades, filtering by minimum size ($10)
        MIN_BET_SIZE = 10
        all_trades = []
        trader_stats = {}  # Track per-trader stats
        game_number_pattern = re.compile(r"\bgame\s*\d+\b", re.IGNORECASE)
        map_number_pattern = re.compile(r"\bmap\s*\d+\b", re.IGNORECASE)
        
        for wallet, trades in wallet_trades.items():
            for trade in trades:
                # Optionally restrict to markets whose title matches a keyword
                title = trade.get("title", "").lower()
                if game_number_pattern.search(title) or map_number_pattern.search(title):
                    continue
                if ONLY_SHOW_MARKET_KEYWORDS:
                    if not any(k.lower() in title for k in ONLY_SHOW_MARKET_KEYWORDS):
                        # Skip trades that are not in the requested market categories
                        continue
                size = trade.get("size", 0)
                
                # Filter out small bets
                if size < MIN_BET_SIZE:
                    continue
                
                all_trades.append(trade)
                
                # Track trader stats
                trader_name = trade.get("name") or trade.get("pseudonym") or wallet[:8]
                if trader_name not in trader_stats:
                    trader_stats[trader_name] = {
                        "wallet": wallet,
                        "trades": 0,
                        "total_size": 0,
                        "avg_price": 0,
                        "prices": []
                    }
                
                trader_stats[trader_name]["trades"] += 1
                trader_stats[trader_name]["total_size"] += size
                trader_stats[trader_name]["prices"].append(trade.get("price", 0.5))
        
        # Calculate average prices
        for trader_name, stats in trader_stats.items():
            if stats["prices"]:
                stats["avg_price"] = sum(stats["prices"]) / len(stats["prices"])
            del stats["prices"]  # Remove temp list
        
        # Store trader stats for later retrieval
        self.trader_stats = trader_stats

        all_markets = self.extract_market_info_from_trades(all_trades)
        logger.info(f"Extracted {len(all_markets)} unique markets from trades")

        # Always filter to non-resolved, non-closed markets from trade metadata
        live_markets = {
            cid: m for cid, m in all_markets.items()
            if not m.get("resolved", False) and not m.get("closed", False)
        }
        logger.info(f"Filtered to {len(live_markets)} markets (not resolved/closed from trade metadata)")

        if not live_markets:
            return {}

        # Group trades by market and count (market_data entries include slug)
        market_data = self.group_trades_by_market(wallet_trades, live_markets)

        # Filter by minimum wallets
        filtered_data = self.filter_by_minimum_wallets(market_data)
        if not filtered_data:
            return {}

        # Filter by majority vote (65%+ on one side)
        # Hedgers are counted in total but not toward the majority
        filtered_data = self.filter_by_majority_vote(filtered_data, threshold=0.65)
        if not filtered_data:
            return {}
        logger.info(f"{len(filtered_data)} markets remain after majority-vote filtering")
        
        # Filter by minimum bet size per trader
        filtered_data = self.filter_by_minimum_bet_size(filtered_data)
        if not filtered_data:
            return {}
        
        # Remove traders who betted on both outcomes (no signal)
        filtered_data = self.filter_traders_on_both_sides(filtered_data)
        if not filtered_data:
            return {}
        
        # Remove traders who have exited their position (bought and sold)
        filtered_data = self.filter_traders_with_exits(filtered_data)
        if not filtered_data:
            return {}

        # Remove highly volatile markets based on outcome entry-price spread
        if ENABLE_VOLATILITY_FILTER:
            filtered_data = self.filter_by_outcome_price_volatility(
                filtered_data,
                max_spread=MAX_OUTCOME_PRICE_SPREAD,
                min_prices=MIN_PRICES_FOR_VOLATILITY_CHECK,
            )
            logger.info(f"{len(filtered_data)} markets remain after volatility filtering")
            if not filtered_data:
                return {}


        
        # Filter by trade age if MAX_MARKET_AGE_HOURS is set
        if MAX_MARKET_AGE_HOURS is not None:
            current_time = time.time()
            max_age_seconds = MAX_MARKET_AGE_HOURS * 3600
            age_filtered = {}
            for mid, data in filtered_data.items():
                latest_ts = data.get("latest_timestamp", 0)
                age_seconds = current_time - latest_ts
                age_hours = age_seconds / 3600
                
                if age_seconds <= max_age_seconds:
                    age_filtered[mid] = data
                    logger.debug(f"✓ {mid} has recent trade ({age_hours:.1f}h ago)")
                else:
                    logger.info(f"✗ {mid} filtered: last trade {age_hours:.1f}h ago (limit: {MAX_MARKET_AGE_HOURS}h)")
            
            filtered_data = age_filtered
            logger.info(f"{len(filtered_data)} markets remain after time-based filtering")
            
            if not filtered_data:
                return {}
        
        # Check external sources to filter out markets that are actually finished
        if CHECK_EXTERNAL_RESULTS:
            external_filtered = {}
            for mid, data in filtered_data.items():
                title = data.get("market_title", "")
                if self.check_external_result(title):
                    logger.info(f"✗ {title[:80]} - appears finished based on external check")
                else:
                    external_filtered[mid] = data
            
            filtered_data = external_filtered
            logger.info(f"{len(filtered_data)} markets remain after external result filtering")
            
            if not filtered_data:
                return {}
        
        # Further filter by checking LIVE status from market pages (optional)
        live_only = {}
        for mid, data in filtered_data.items():
            slug = data.get("slug")
            if not slug:
                logger.debug(f"Skipping {mid} — no slug to check live status")
                continue
            if CHECK_LIVE_STATUS:
                # Fetch current market status from page
                status = self.get_market_live_status(slug)

                # Only include if NOT resolved AND NOT closed (i.e., LIVE)
                if not status["resolved"] and not status["closed"]:
                    live_only[mid] = data
                    logger.debug(f"✓ {mid} is LIVE (slug={slug})")
                else:
                    reason = []
                    if status["resolved"]:
                        reason.append("resolved")
                    if status["closed"]:
                        reason.append("closed")
                    logger.info(f"✗ {mid} NOT LIVE: {', '.join(reason)} (slug={slug})")

                # Polite but faster pacing
                time.sleep(0.05)
            else:
                # If not checking page status, include the market as-is
                live_only[mid] = data

        logger.info(f"{len(live_only)} markets remain after LIVE status filtering")
        return live_only