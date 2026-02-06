"""Main entry point for Polymarket analysis."""

import sys
import pandas as pd
from config import (
    TRACKED_WALLETS, OUTPUT_CSV, MIN_WALLETS_PER_MARKET, TRADER_RATINGS,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ENABLE_TELEGRAM_NOTIFICATIONS
)
from api import PolymarketAPI
from processor import TradeProcessor
from analyzer import PolymarketAnalyzer
from notifier import TelegramNotifier
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    try:
        logger.info("=" * 70)
        logger.info("Polymarket LIVE Trades Analysis - Top 600 Most Recent Trades")
        logger.info("=" * 70)
        
        # Initialize components
        api = PolymarketAPI()
        processor = TradeProcessor(min_wallets=MIN_WALLETS_PER_MARKET)
        analyzer = PolymarketAnalyzer(api, processor)
        
        # Run analysis
        results_df = analyzer.analyze(TRACKED_WALLETS)
        
        # Display results
        if len(results_df) > 0:
            logger.info("\nResults:")
            
            # Show trader summary if available
            trader_stats = analyzer.processor.trader_stats
            if trader_stats:
                trader_results = []
                for trader_name, stats in sorted(trader_stats.items(), key=lambda x: x[1]["total_size"], reverse=True):
                    rating = TRADER_RATINGS.get(trader_name, "-")
                    rating_str = f"{rating}/10" if isinstance(rating, int) else rating
                    trader_results.append({
                        "Trader": trader_name,
                        "Rating": rating_str,
                        "Bets": stats["trades"],
                        "Avg Entry Price": f"${stats['avg_price']:.3f}",
                        "Total Size": f"${stats['total_size']:.2f}",
                    })
                trader_df = pd.DataFrame(trader_results)
                print("\n" + "=" * 100)
                print("TRADER SUMMARY")
                print("=" * 100)
                print(trader_df.to_string(index=False))
            
            # Show markets (hide Market ID and Latest Trade timestamp in console output)
            print("\n" + "=" * 100)
            print("MARKETS")
            print("=" * 100)
            printable_df = results_df.copy()
            columns_to_drop = []
            if "Market ID" in printable_df.columns:
                columns_to_drop.append("Market ID")
            if "Latest Trade" in printable_df.columns:
                columns_to_drop.append("Latest Trade")
            if columns_to_drop:
                printable_df = printable_df.drop(columns=columns_to_drop)

            # Build rows and split outcomes into left/right for alignment
            rows = printable_df.to_dict(orient="records")
            parsed = []
            for r in rows:
                title = str(r.get("Market Title", ""))
                outcomes = str(r.get("Outcomes", ""))
                if "|" in outcomes:
                    parts = outcomes.split("|", 1)
                    left = parts[0].strip()
                    right = parts[1].strip()
                else:
                    left = outcomes.strip()
                    right = ""
                wallets = str(r.get("Total Wallets", ""))
                parsed.append({"title": title, "left": left, "right": right, "wallets": wallets})

            # Compute column widths
            title_w = max([len(p["title"]) for p in parsed] + [12])
            left_w = max([len(p["left"]) for p in parsed] + [4])
            right_w = max([len(p["right"]) for p in parsed] + [0])
            wallets_w = max([len(p["wallets"]) for p in parsed] + [13])

            # Header
            header_parts = [f"{'Market Title':<{title_w}}", f"{'Outcome':<{left_w}}"]
            if right_w > 0:
                header_parts.append(f"{'Opposite':<{right_w}}")
            header_parts.append(f"{'Total Wallets':>{wallets_w}}")
            print("  ".join(header_parts))
            print("-" * (title_w + left_w + right_w + wallets_w + 6))

            # Rows
            for p in parsed:
                if right_w > 0:
                    out_part = f"{p['left']:<{left_w}} | {p['right']:<{right_w}}"
                else:
                    out_part = f"{p['left']:<{left_w}}"
                print(f"{p['title']:<{title_w}}  {out_part}  {p['wallets']:>{wallets_w}}")
            print("=" * 100)

            # Export to CSV
            analyzer.export_csv(results_df, OUTPUT_CSV)
            print(f"\nCSV exported to: {OUTPUT_CSV}")
            
            # Send Telegram notification with top 4 markets
            if ENABLE_TELEGRAM_NOTIFICATIONS:
                notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
                notifier.send_top_markets(results_df, top_n=4)
        else:
            print("\nNo LIVE markets found matching criteria.")
            
            # Notify about no results
            if ENABLE_TELEGRAM_NOTIFICATIONS:
                notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
                notifier.send_message("⚠️ Ingen markets funnet i denne kjøringen.")
        
        api.close()
        logger.info("Analysis completed successfully")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
