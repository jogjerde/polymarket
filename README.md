# Polymarket LIVE Trades Analyzer

A Python project that analyzes LIVE Polymarket trades across tracked wallet addresses, identifying markets where multiple wallets are actively trading.

## Project Structure

```
polymarket/
├── main.py                          # Entry point
├── run.py                           # Alternative execution wrapper
├── config.py                        # Configuration (wallets, API endpoints)
├── api.py                           # API interaction module
├── processor.py                     # Data processing and aggregation
├── analyzer.py                      # Main analysis orchestration
├── debug.py                         # Debug utilities
├── requirements.txt                 # Python dependencies
├── polymarket_trades_analysis.csv   # Output file (generated)
└── README.md                        # This file
```

## Features

- **Multi-wallet tracking**: Monitor up to 7 wallet addresses simultaneously
- **LIVE market filtering**: Only analyze unresolved, open markets (resolved=false, closed=false)
- **Smart aggregation**: Group trades by market and count YES/NO positions per wallet
- **Minimum wallet threshold**: Display only markets with 2+ tracked wallets
- **CSV export**: Automatically save results for further analysis
- **Comprehensive logging**: Track API calls and data processing steps

## Requirements

- Python 3.7+
- requests (HTTP library)
- pandas (Data analysis)

## Installation

1. Clone or download this project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.py` to customize:

### Tracked Wallets
```python
TRACKED_WALLETS = [
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

## Usage

### Quick Start
```bash
python main.py
```

### With Custom Script
```bash
python run.py
```

### Output

The analyzer produces:
1. **Console output**: Formatted DataFrame with results
2. **CSV file**: `polymarket_trades_analysis.csv` with all results

## Output Columns

| Column | Description |
|--------|-------------|
| Market Title | Human-readable market name |
| Market ID | Polymarket condition ID (unique identifier) |
| YES Count | Number of tracked wallets with YES positions |
| NO Count | Number of tracked wallets with NO positions |
| Total Wallets | Total unique wallets involved in market |

## Example Output

```
Market Title                                     Market ID                                       YES Count  NO Count  Total Wallets
No change in Fed interest rates after May 2025   0xffffb2874475ae9c1e3a0e3c3c4b4e329...          3          0          3
Will Zelenskyy wear a suit before July?          0x655e5ca101c466b6293aa15e06173b78...          0          3          3
Will Mark Carney be next Canadian PM?            0x87822b3d4ccba1835d698354b01c050...          3          0          3
```

## API Data Source

All data is fetched from the public Polymarket API (no authentication required):

- **Trades API**: `GET https://data-api.polymarket.com/trades?user=WALLET_ADDRESS`
  - Returns up to 100 recent trades per wallet
  - Includes market metadata, outcomes, and trade details

## How It Works

### Algorithm

1. **Fetch Trades**: Retrieve all recent trades for each tracked wallet
2. **Extract Markets**: Identify unique markets from the trades
3. **Filter LIVE Markets**: Keep only markets where:
   - `resolved == false` (outcome not yet determined)
   - `closed == false` (market still accepting trades)
4. **Group by Market**: Aggregate trades by market ID
5. **Count Positions**: Tally YES/NO positions per wallet
6. **Filter by Wallets**: Show only markets with ≥2 wallets involved
7. **Sort & Export**: Sort by total wallets and export to CSV

### Data Fields Used

From each trade record:
- `conditionId`: Unique market identifier
- `outcome`: "Yes" or "No" (user's position)
- `title`: Human-readable market name
- `resolved`: Whether market outcome is determined
- `closed`: Whether market accepts new trades

## Limitations

- Trades API returns latest ~100 trades per wallet (not paginated)
- No category filtering applied
- Markets are determined by conditions found in trade history
- Focuses on accuracy over trading strategy insights

## Troubleshooting

### No LIVE Markets Found
- Check that wallet addresses in `config.py` are correct
- Verify wallets have recent trading activity
- Confirm internet connection to Polymarket API

### ImportError for pandas/requests
```bash
pip install -r requirements.txt
```

### Empty Results
- May indicate no current LIVE markets match the criteria
- Try reducing `MIN_WALLETS_PER_MARKET` in config.py
- Check that tracked wallets are actively trading

## Performance Notes

- API calls are rate-limited (no explicit limits documented by Polymarket)
- Typical execution time: 5-10 seconds for 7 wallets
- Memory usage: Minimal (~50MB for 700 trades)

## Notes

- No category filtering - analyzes all available markets
- Focus on data fetching accuracy and grouping logic
- Trades data is real-time from Polymarket API
- No local caching or persistence (fresh data on each run)
- CSV format is compatible with Excel, Google Sheets, and other tools

## License

This project is provided as-is for analysis purposes.

## Support

For questions about:
- **Polymarket API**: See [Polymarket Documentation](https://polymarket.com)
- **Code modifications**: Review the module docstrings
- **Data interpretation**: Check the output column descriptions above

