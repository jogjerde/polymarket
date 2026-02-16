"""Configuration for Polymarket analysis."""

# Wallet addresses to track. REMEMBER, it shouldn't be users who micromanage throughout the process. For example by selling early when they are losing.
TRACKED_WALLETS = [
    "0xf5b723a4a8efb369f4db1228eb7ba9279c353e1c",  # fabiplouf
    "0x2005d16a84ceefa912d4e380cd32e7ff827875ea",  # RN1
    "0xea9e60763ce2e27294d869f2fd24020b5188d3fb",  # IForgiveYou
    "0x1c5575dc20e4ea54d1bb09ccda72ccf8a3b684ce",  # b00k13
    "0x68146921df11eab44296dc4e58025ca84741a9e7",  # LynxTitan
    "0xe42bf69ebd99d9c47d56b58930d3972b3a687ea9",  # lilJerry
    "0x7d5d15335ec60449995971a563fd94e060f091d8",  # SILF
    "0x5bc1f038c4cd8344bc97f542bf90b9babb5d9932",  # weepingangel89
    "0x1ee07513d91d3e4ba7e4a119aa7cd379605eae41",  # PresidentDonaldPump
    "0x581d24e58039e1f569dacde9c288e028b51f2b06",  # Duratio
    "0x8c0b024c17831a0dde038547b7e791ae6a0d7aa5",  # IBOV200K
    "0x43372356634781eea88d61bbdd7824cdce958882",  # Anjun
    "0xeffd76b6a4318d50c6f71a16b276c5b279445a86",  # Xero100
    "0x97e12cc7391a50e49042b44a2d4a0cef54c8017b",  # BigBlackGorilla
    "0x3212a515f3a02546830a6fb41f01470ccfff634e",  # beifengcc
    "0x583f70da7ee63bc1562e945f99c3407ffd622dab",  # account3333
    "0xfdc0bd67fbd71aa8edd00121eb2a7fcbddc34b85",  # oneheadedtiger
    "0x44c58184f89a5c2f699dc8943009cb3d75a08d45",  # JhonAlexanderHinestroza
    "0xec981ed70ae69c5cbcac08c1ba063e734f6bafcd",  # 0xheavy888
    "0x9c82c60829df081d593055ee5fa288870c051f13",  # Vetch
    "0x2cad53bb58c266ea91eea0d7ca54303a10bceb66",  # JustBeHappyxd
    "0x18670d5a83b7b38d509398067c095d4c321992ca",  # Trapital
    "0xac9b386454ed02ef205e0ebd189d8864fd02d4c5",  # tryingmyluckhere
    "0xbdd2bbcbf179cf9b0062b747fbc17755b9b00bd8",  # abuzzin
    "0xc20c56eb62bd257d73e0a52e09d7661a11d5fdb5",  # PavMM  (sells early when losing)
    "0x1e524ff2123d380a690dbdf2245de2a9428e91d6",  # rocky42002
    "0xd410ddf625bbfc1952eef4c5973b50acd9393a1b",  # Viacheslav92
    "0x5c85faa9e70e32ee227ce318906f81fc67185cd6",  # shiwanfute
    "0x95a9ff7399a389428a9a9deb6f416c635d2b4352",  # AtiradorFreestyle
]

# Trader ratings (1-10 scale) - used for filtering and display
TRADER_RATINGS = {
    "fabiplouf": 9,
    "RN1": 9,
    "IForgiveYou": 5,
    "b00k13": 3,
    "LynxTitan": 2,
    "lilJerry": 7,
    "SILF": 9,
    "weepingangel89": 5,
    "PresidentDonaldPump": 4,
    "Duratio": 2,
    "IBOV200K": 5,
    "Anjun": 4,
    "Xero100": 3,
    "BigBlackGorilla": 8,
    "beifengcc": 8,
    "account3333": 8,
    "oneheadedtiger": 7,
    "JhonAlexanderHinestroza": 9,
    "0xheavy888": 4,
    "Vetch": 6,
    "JustBeHappyxd": 7,
    "Trapital": 5,
    "tryingmyluckhere": 2,
    "abuzzin": 5,
    "PavMM": 1,
    "rocky42002": 1,
    "Viacheslav92": 3,
    "shiwanfute": 2,
    "AtiradorFreestyle": 1,
}

# API endpoints
POLYMARKET_API_BASE = "https://data-api.polymarket.com"
TRADES_ENDPOINT = f"{POLYMARKET_API_BASE}/trades"
MARKETS_ENDPOINT = f"{POLYMARKET_API_BASE}/markets"

# Output settings
OUTPUT_CSV = "polymarket_trades_analysis.csv"
MIN_WALLETS_PER_MARKET = 2
# If False, do not attempt to check market page status; include all markets
# referenced in tracked wallets' trades. Set to True to filter to markets
# that appear to be LIVE (not resolved/closed).
CHECK_LIVE_STATUS = False

# Optional market keyword filter: when set to a non-empty list, only trades
# whose market title contains any of these keywords (case-insensitive)
# will be included in analysis. For example, ['lol'] will restrict output
# to League of Legends markets whose titles include 'LoL' or 'lol'.
ONLY_SHOW_MARKET_KEYWORDS = []

# Maximum age in hours for a market's last trade to be considered "active"
# Markets with no trades in this timeframe will be filtered out
# Set to None to disable time-based filtering
MAX_MARKET_AGE_HOURS = 6

# Check external sources to verify if markets are actually resolved
# This will attempt to scrape results from esports/sports websites
CHECK_EXTERNAL_RESULTS = False
# Minimum bet size per trader (in dollars)
# Bets smaller than this will be filtered out, unless probability is very low (under 10%)
MIN_BET_SIZE_PER_TRADER = {
    "fabiplouf": 1,
    "RN1": 80,
    "IForgiveYou": 6,
    "b00k13": 5,
    "LynxTitan": 40,
    "lilJerry": 100,
    "SILF": 99,
    "weepingangel89": 12,
    "PresidentDonaldPump": 40,
    "Duratio": 0,
    "IBOV200K": 5,
    "Anjun": 5,
    "Xero100": 8,
    "BigBlackGorilla": 14,
    "beifengcc": 6,
    "account3333": 4,
    "oneheadedtiger": 8,
    "JhonAlexanderHinestroza": 500,
    "0xheavy888": 150,
    "Vetch": 70,
    "JustBeHappyxd": 200,
    "Trapital": 500,
    "tryingmyluckhere": 50,
    "abuzzin": 110,
    "PavMM": 50,
    "rocky42002": 50,
    "Viacheslav92": 50,
    "shiwanfute": 50,
    "AtiradorFreestyle": 50,
}

# Volatility filter: remove markets where traders enter the same outcome
# at very different prices (example: around 0.50 and 0.20).
ENABLE_VOLATILITY_FILTER = True

# Maximum allowed spread for prices on the same outcome.
# If max(price) - min(price) is above this, the market is filtered out.
MAX_OUTCOME_PRICE_SPREAD = 0.25

# Only evaluate volatility on outcomes that have at least this many prices.
MIN_PRICES_FOR_VOLATILITY_CHECK = 2

# If True, show individual MMR ratings for each trader and total $ per outcome
# If False, show average MMR
SHOW_INDIVIDUAL_RATINGS = True

# Telegram notification settings
# Get bot token from @BotFather on Telegram
# Get chat ID by messaging @userinfobot on Telegram
TELEGRAM_BOT_TOKEN = "8395273058:AAGEGxcT03W80zL5rMjshMXP2NH-AAaJcto"
TELEGRAM_CHAT_ID = "8509374331"
ENABLE_TELEGRAM_NOTIFICATIONS = True