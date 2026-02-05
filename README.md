# Polymarket Expert Trader Signal Analyzer

A Python tool that tracks and analyzes positions from elite Polymarket traders, providing high-quality trading signals by filtering out noise and showing only active, meaningful bets.

## Project Structure

```
polymarket/
├── main.py                          # Entry point - run the analysis
├── config.py                        # Configuration (tracked wallets, ratings, thresholds)
├── api.py                           # Polymarket API interaction
├── processor.py                     # Trade processing, filtering, and aggregation
├── analyzer.py                      # Results formatting and display
├── requirements.txt                 # Python dependencies
├── polymarket_trades_analysis.csv   # Output file (auto-generated)
└── README.md                        # This file
```

## Features

### Signal Quality Filters
- **22 Elite Traders Tracked**: Monitor top-rated traders (ratings 1-10) with proven track records
- **Time-Based Filtering**: Only show markets with trades in the last 6 hours (configurable)
- **Minimum Bet Size per Trader**: Filter out small, low-conviction bets (configurable per trader)
- **Arbitrage Detection**: Remove traders betting on both sides of the same market
- **Exit Detection**: Filter out positions where traders have sold (bought then sold = no signal)
- **Active Markets Only**: Automatically exclude resolved or closed markets

### Display Features
- **Individual Trader Ratings**: See each trader's rating in brackets `[9 8 7]`
- **Position Sizes**: Total dollar amount invested per outcome
- **Entry Prices**: Average price at which traders entered their positions
- **Trader Summary**: Overview of all active traders with total sizes and entry prices

## Requirements

- Python 3.7+
- requests (HTTP library)
- pandas (Data analysis and CSV export)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jogjerde/polymarket.git
cd polymarket
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Simply run the main script:
```bash
python main.py
```

The tool will:
1. Fetch the 100 most recent trades for each of the 22 tracked wallets (2,200 trades total)
2. Filter to the 600 most recent trades
3. Apply all quality filters (time, size, arbitrage, exits, etc.)
4. Display results in the terminal
5. Export to `polymarket_trades_analysis.csv`

### Example Output

```
====================================================================================================
TRADER SUMMARY
====================================================================================================
                 Trader Rating  Bets Avg Entry Price Total Size
                    RN1   9/10    78          $0.533 $190259.34
               IBOV200K   5/10    32          $0.445 $145976.18
        BigBlackGorilla   8/10    32          $0.567 $111442.60
                  
====================================================================================================
MARKETS
====================================================================================================
Market Title                                                    Outcome                            
----------------------------------------------------------------------------------------------------
Dota 2: Team Liquid vs Heroic (BO1) - BLAST Slam Group Stage   HEROIC: [8 7 4] $8086 ($0.397)
Transylvania Open: Anastasia Potapova vs Sorana Cirstea        CIRSTEA: [9] $32379 ($0.640) | POTAPOVA: [2] $200 ($0.001)
```

**Reading the output:**
- `[8 7 4]` = Individual trader ratings who bet on this outcome
- `$8086` = Total dollar amount invested
- `($0.397)` = Average entry price

## Configuration

Edit `config.py` to customize the behavior:

### Key Settings

```python
# Tracked wallets (22 elite traders)
TRACKED_WALLETS = [
    "0xf5b723a4a8efb369f4db1228eb7ba9279c353e1c",  # RN1
    "0x2005d16a84ceefa912d4e380cd32e7ff827875ea",  # IBOV200K
    # ... 20 more
]

# Trader quality ratings (1-10 scale)
TRADER_RATINGS = {
    "RN1": 9,
    "IBOV200K": 5,
    "BigBlackGorilla": 8,
    # ... etc
}

# Minimum bet size per trader (filters low-conviction bets)
MIN_BET_SIZE_PER_TRADER = {
    "RN1": 0,
    "Trapital": 500,  # High-volume trader, only show large bets
    # ... etc
}

# Time window for "active" markets
MAX_MARKET_AGE_HOURS = 6  # Only show markets with trades in last 6 hours

# Minimum wallets required to display a market
MIN_WALLETS_PER_MARKET = 2

# Display settings
SHOW_INDIVIDUAL_RATINGS = True  # Show [7 8 5] format instead of average
```

### Advanced Filtering

The tool automatically applies several filters to ensure signal quality:

1. **Time Filter**: Markets must have trades within `MAX_MARKET_AGE_HOURS`
2. **Size Filter**: Each trader's bet must exceed their `MIN_BET_SIZE_PER_TRADER` threshold
3. **Arbitrage Filter**: Removes traders betting on multiple outcomes in the same market
4. **Exit Filter**: Removes traders who have both BUY and SELL trades (closed position)
5. **Market State Filter**: Only shows open, unresolved markets from trade metadata

### Performance Settings

```python
# Disable slow external checks (enabled by default for speed)
CHECK_LIVE_STATUS = False        # Skip HTTP requests to polymarket.com
CHECK_EXTERNAL_RESULTS = False   # Skip external result verification
```
    "0xb30fe15964655f469c29a0b7b7a7305ff02a9505",
    # Add/remove wallet addresses as needed
]
```

### Minimum Wallets Per Market
```python
MIN_WALLETS_PER_MARKET = 2  # Only show markets with 2+ wallets
```

### Output Settings
```python
OUTPUT_CSV = "polymarket_trades_analysis.csv"  # Output filename
```

## How It Works

### Data Pipeline

1. **Fetch Trades**: Retrieves 100 most recent trades for each tracked wallet via Polymarket API
2. **Time Filter**: Keeps only the 600 most recent trades across all wallets
3. **Market Extraction**: Groups trades by `condition_id` (unique market identifier)
4. **Initial Filtering**: Removes resolved/closed markets based on trade metadata
5. **Aggregation**: Groups by market, tracks traders per outcome with sizes and prices
6. **Quality Filters**:
   - Minimum wallet count (default: 2+ traders per market)
   - Minimum bet size per trader (configurable per trader)
   - Arbitrage removal (traders on both sides)
   - Exit detection (traders with BUY + SELL)
   - Time-based filtering (last 6 hours)
7. **Format & Display**: Shows results with ratings, sizes, and entry prices

### Signal Quality Philosophy

The tool is designed to show only **high-conviction, active positions** from elite traders:

- **No small bets**: Filter out "test" bets or low-conviction positions
- **No arbitrage**: Traders betting both sides provide no directional signal
- **No exits**: Closed positions mean the trader changed their mind
- **Recent only**: Old trades may be stale as market conditions change
- **Rated traders**: 1-10 scale helps weight signal quality

## Output Files

- **Console**: Formatted tables with trader summary and markets
- **CSV**: `polymarket_trades_analysis.csv` with all market data for further analysis

## Performance

- Runtime: ~5-6 seconds for 22 wallets
- API calls: 22 wallet fetches (100 trades each) = 2,200 trades fetched
- Processing: Filters down to ~10-20 high-quality active markets

## Troubleshooting

### "No markets found"
- Check `MAX_MARKET_AGE_HOURS` - might be too restrictive
- Verify traders are active (check their recent trades manually)
- Lower `MIN_BET_SIZE_PER_TRADER` thresholds if too strict

### Slow performance
- Ensure `CHECK_LIVE_STATUS = False` and `CHECK_EXTERNAL_RESULTS = False`
- These add HTTP requests which slow down significantly

### Missing traders in output
- Check `MIN_BET_SIZE_PER_TRADER` - their bets might be filtered
- Verify they haven't exited positions (BUY + SELL on same market)
- Check if they're betting on both sides (arbitrage filter)

## License

MIT

## Contributing

Feel free to submit issues or pull requests for improvements!

## Limitations

- Trades API returns latest ~100 trades per wallet (not paginated)
- No category filtering applied
## License

MIT

## Contributing

Feel free to submit issues or pull requests for improvements!

