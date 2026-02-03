"""Constants for the CoinMarketCap integration."""

DOMAIN = "coinmarketcap"

CONF_API_KEY = "api_key"
CONF_SYMBOLS = "symbols"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_DECIMALS = "decimals"
CONF_SHOW_SENSORS = "show_sensors"
CONF_CURRENCY = "currency"

DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
DEFAULT_DECIMALS = 2
DEFAULT_CURRENCY = "USD"
DEFAULT_SENSORS = ["price", "percent_change_24h", "credits_left_month"]

CURRENCIES = ["USD", "EUR", "GBP", "BTC", "ETH"]

# API Endpoints
API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
GLOBAL_API_URL = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
FEAR_GREED_API_URL = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest"
KEY_INFO_API_URL = "https://pro-api.coinmarketcap.com/v1/key/info"

SENSOR_TYPES = {
    # Cryptocurrency Symbols
    "price": {
        "name": "Price",
        "json_path": ["quote", "{currency}", "price"],
        "unit": "{currency_symbol}",
        "icon": "mdi:cash",
        "category": "symbol",
        "device_class": "monetary",
        "state_class": "measurement"
    },
    "percent_change_1h": {
        "name": "1h Change",
        "json_path": ["quote", "{currency}", "percent_change_1h"],
        "unit": "%",
        "icon": "mdi:chart-line-variant",
        "category": "symbol",
        "state_class": "measurement"
    },
    "percent_change_24h": {
        "name": "24h Change",
        "json_path": ["quote", "{currency}", "percent_change_24h"],
        "unit": "%",
        "icon": "mdi:chart-line",
        "category": "symbol",
        "state_class": "measurement"
    },
    "percent_change_7d": {
        "name": "7d Change",
        "json_path": ["quote", "{currency}", "percent_change_7d"],
        "unit": "%",
        "icon": "mdi:calendar-week",
        "category": "symbol",
        "state_class": "measurement"
    },
    "percent_change_30d": {
        "name": "30d Change",
        "json_path": ["quote", "{currency}", "percent_change_30d"],
        "unit": "%",
        "icon": "mdi:calendar-month",
        "category": "symbol",
        "state_class": "measurement"
    },
    "volume_24h": {
        "name": "Volume 24h",
        "json_path": ["quote", "{currency}", "volume_24h"],
        "unit": "{currency_symbol}",
        "icon": "mdi:chart-bar",
        "category": "symbol",
        "device_class": "monetary",
        "state_class": "measurement"
    },
    "volume_change_24h": {
        "name": "Volume Change 24h",
        "json_path": ["quote", "{currency}", "volume_change_24h"],
        "unit": "%",
        "icon": "mdi:chart-bell-curve",
        "category": "symbol",
        "state_class": "measurement"
    },
    "market_cap": {
        "name": "Market Cap",
        "json_path": ["quote", "{currency}", "market_cap"],
        "unit": "{currency_symbol}",
        "icon": "mdi:chart-pie",
        "category": "symbol",
        "device_class": "monetary",
        "state_class": "measurement"
    },
    "market_cap_dominance": {
        "name": "Market Cap Dominance",
        "json_path": ["quote", "{currency}", "market_cap_dominance"],
        "unit": "%",
        "icon": "mdi:chart-donut",
        "category": "symbol",
        "state_class": "measurement"
    },
    "circulating_supply": {
        "name": "Circulating Supply",
        "json_path": ["circulating_supply"],
        "unit": None,
        "icon": "mdi:coins",
        "category": "symbol",
        "state_class": "measurement",
        "entity_category": "diagnostic"
    },
    "total_supply": {
        "name": "Total Supply",
        "json_path": ["total_supply"],
        "unit": None,
        "icon": "mdi:safe",
        "category": "symbol",
        "state_class": "measurement",
        "entity_category": "diagnostic"
    },
    "max_supply": {
        "name": "Max Supply",
        "json_path": ["max_supply"],
        "unit": None,
        "icon": "mdi:database",
        "category": "symbol",
        "state_class": "measurement",
        "entity_category": "diagnostic"
    },
    "cmc_rank": {
        "name": "Rank",
        "json_path": ["cmc_rank"],
        "unit": None,
        "icon": "mdi:trophy",
        "category": "symbol",
        "state_class": "measurement",
        "entity_category": "diagnostic"
    },
    
    # Global Metrics
    "btc_dominance": {
        "name": "BTC Dominance",
        "json_path": ["btc_dominance"],
        "unit": "%",
        "icon": "mdi:currency-btc",
        "category": "global",
        "state_class": "measurement"
    },
    "eth_dominance": {
        "name": "ETH Dominance",
        "json_path": ["eth_dominance"],
        "unit": "%",
        "icon": "mdi:currency-eth",
        "category": "global",
        "state_class": "measurement"
    },
    "total_market_cap": {
        "name": "Total Market Cap",
        "json_path": ["quote", "{currency}", "total_market_cap"],
        "unit": "{currency_symbol}",
        "icon": "mdi:earth",
        "category": "global",
        "device_class": "monetary",
        "state_class": "measurement"
    },
    "total_volume_24h": {
        "name": "Total Volume 24h",
        "json_path": ["quote", "{currency}", "total_volume_24h"],
        "unit": "{currency_symbol}",
        "icon": "mdi:chart-line-variant",
        "category": "global",
        "device_class": "monetary",
        "state_class": "measurement"
    },
    
    # Fear & Greed Index
    "fear_greed_index": {
        "name": "Fear & Greed Index",
        "json_path": ["value"],
        "unit": None,
        "icon": "mdi:emoticon-neutral",
        "category": "fear_greed",
        "state_class": "measurement"
    },
    "fear_greed_classification": {
        "name": "Fear & Greed classification",
        "json_path": ["value_classification"],
        "unit": None,
        "icon": "mdi:label",
        "category": "fear_greed"
    },
    
    # API Usage (Key Info)
    "credits_used_day": {
        "name": "Credits Used Today",
        "json_path": ["usage", "current_day", "credits_used"],
        "unit": "Credits",
        "icon": "mdi:api",
        "category": "key_info",
        "state_class": "total_increasing",
        "entity_category": "diagnostic"
    },
    "credits_left_day": {
        "name": "Credits Left Today",
        "json_path": ["usage", "current_day", "credits_left"],
        "unit": "Credits",
        "icon": "mdi:api-off",
        "category": "key_info",
        "state_class": "measurement",
        "entity_category": "diagnostic"
    },
    "credits_used_month": {
        "name": "Credits Used Month",
        "json_path": ["usage", "current_month", "credits_used"],
        "unit": "Credits",
        "icon": "mdi:calendar-check",
        "category": "key_info",
        "state_class": "total_increasing",
        "entity_category": "diagnostic"
    },
    "credits_left_month": {
        "name": "Credits Left Month",
        "json_path": ["usage", "current_month", "credits_left"],
        "unit": "Credits",
        "icon": "mdi:calendar-remove",
        "category": "key_info",
        "state_class": "measurement",
        "entity_category": "diagnostic"
    }
}
