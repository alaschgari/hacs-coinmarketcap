"""Constants for the CoinMarketCap integration."""

DOMAIN = "coinmarketcap"

CONF_API_KEY = "api_key"
CONF_SYMBOLS = "symbols"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_DECIMALS = "decimals"
CONF_SHOW_SENSORS = "show_sensors"

DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
DEFAULT_DECIMALS = 2
DEFAULT_SENSORS = ["price", "percent_change_24h"]

# API Endpoints
API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
GLOBAL_API_URL = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
FEAR_GREED_API_URL = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest"

SENSOR_TYPES = {
    # Cryptocurrency Symbols
    "price": {
        "name": "Price",
        "json_path": ["quote", "USD", "price"],
        "unit": "$",
        "icon": "mdi:cash",
        "category": "symbol"
    },
    "percent_change_1h": {
        "name": "1h Change",
        "json_path": ["quote", "USD", "percent_change_1h"],
        "unit": "%",
        "icon": "mdi:chart-line-variant",
        "category": "symbol"
    },
    "percent_change_24h": {
        "name": "24h Change",
        "json_path": ["quote", "USD", "percent_change_24h"],
        "unit": "%",
        "icon": "mdi:chart-line",
        "category": "symbol"
    },
    "percent_change_7d": {
        "name": "7d Change",
        "json_path": ["quote", "USD", "percent_change_7d"],
        "unit": "%",
        "icon": "mdi:calendar-week",
        "category": "symbol"
    },
    "percent_change_30d": {
        "name": "30d Change",
        "json_path": ["quote", "USD", "percent_change_30d"],
        "unit": "%",
        "icon": "mdi:calendar-month",
        "category": "symbol"
    },
    "volume_24h": {
        "name": "Volume 24h",
        "json_path": ["quote", "USD", "volume_24h"],
        "unit": "$",
        "icon": "mdi:chart-bar",
        "category": "symbol"
    },
    "volume_change_24h": {
        "name": "Volume Change 24h",
        "json_path": ["quote", "USD", "volume_change_24h"],
        "unit": "%",
        "icon": "mdi:chart-bell-curve",
        "category": "symbol"
    },
    "market_cap": {
        "name": "Market Cap",
        "json_path": ["quote", "USD", "market_cap"],
        "unit": "$",
        "icon": "mdi:chart-pie",
        "category": "symbol"
    },
    "market_cap_dominance": {
        "name": "Market Cap Dominance",
        "json_path": ["quote", "USD", "market_cap_dominance"],
        "unit": "%",
        "icon": "mdi:chart-donut",
        "category": "symbol"
    },
    "circulating_supply": {
        "name": "Circulating Supply",
        "json_path": ["circulating_supply"],
        "unit": None,
        "icon": "mdi:coins",
        "category": "symbol"
    },
    "total_supply": {
        "name": "Total Supply",
        "json_path": ["total_supply"],
        "unit": None,
        "icon": "mdi:safe",
        "category": "symbol"
    },
    "max_supply": {
        "name": "Max Supply",
        "json_path": ["max_supply"],
        "unit": None,
        "icon": "mdi:database",
        "category": "symbol"
    },
    "cmc_rank": {
        "name": "Rank",
        "json_path": ["cmc_rank"],
        "unit": None,
        "icon": "mdi:trophy",
        "category": "symbol"
    },
    
    # Global Metrics
    "btc_dominance": {
        "name": "BTC Dominance",
        "json_path": ["btc_dominance"],
        "unit": "%",
        "icon": "mdi:currency-btc",
        "category": "global"
    },
    "eth_dominance": {
        "name": "ETH Dominance",
        "json_path": ["eth_dominance"],
        "unit": "%",
        "icon": "mdi:currency-eth",
        "category": "global"
    },
    "total_market_cap": {
        "name": "Total Market Cap",
        "json_path": ["quote", "USD", "total_market_cap"],
        "unit": "$",
        "icon": "mdi:earth",
        "category": "global"
    },
    "total_volume_24h": {
        "name": "Total Volume 24h",
        "json_path": ["quote", "USD", "total_volume_24h"],
        "unit": "$",
        "icon": "mdi:chart-line-variant",
        "category": "global"
    },
    
    # Fear & Greed Index
    "fear_greed_index": {
        "name": "Fear & Greed Index",
        "json_path": ["value"],
        "unit": None,
        "icon": "mdi:emoticon-neutral",
        "category": "fear_greed"
    },
    "fear_greed_classification": {
        "name": "Fear & Greed classification",
        "json_path": ["value_classification"],
        "unit": None,
        "icon": "mdi:label",
        "category": "fear_greed"
    }
}
