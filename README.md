# CoinMarketCap Integration for Home Assistant

<p align="center">
  <img src="https://raw.githubusercontent.com/alaschgari/hacs-coinmarketcap/main/logo.png" alt="CoinMarketCap Logo" width="200" height="200">
</p>

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-orange.svg)](https://www.buymeacoffee.com/alaschgari)

This custom integration for Home Assistant allows you to track cryptocurrency prices and market data using the CoinMarketCap API.
 
## Prerequisites
To use this integration, you need a **CoinMarketCap Pro API Key**.
- You can get a free API key (Basic Plan) by signing up at [coinmarketcap.com/api/](https://coinmarketcap.com/api/).
- Once registered, you will find your API key in the [CoinMarketCap Developer Dashboard](https://pro.coinmarketcap.com/account/).

## Features
- Real-time price tracking in USD.
- 24h percent change sensors.
- Additional attributes like Market Cap and 24h Volume.
- Global market metrics (BTC/ETH Dominance, Total Market Cap).
- Fear & Greed Index sentiment tracking.
- Easy configuration via Home Assistant UI.

## Supported API Endpoints
This integration utilizes the following CoinMarketCap Professional API endpoints:
- **Quotes Latest**: `/v1/cryptocurrency/quotes/latest` (Price, Volume, Market Cap)
- **Global Metrics Latest**: `/v1/global-metrics/quotes/latest` (BTC/ETH Dominance, Total Market Cap)
- **Fear & Greed Latest**: `/v3/fear-and-greed/latest` (Sentiment Index)

## Installation via HACS
1. Open HACS in your Home Assistant instance.
2. Click on "Integrations".
3. Click the three dots in the upper right corner and select "Custom repositories".
4. Add the URL of this repository (`https://github.com/alaschgari/hacs-coinmarketcap`) and select "Integration" as the category.
5. Click "Add" and then install the "CoinMarketCap" integration.
6. Restart Home Assistant.

## Configuration
1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for **CoinMarketCap**.
4. Enter your **API Key** (from [pro.coinmarketcap.com](https://pro.coinmarketcap.com/account/)) and the **Symbols** (comma-separated, e.g., `BTC,ETH,SOL`) you want to track.

## Support

If you find this integration useful and want to support its development, you can buy me a coffee! Your support is greatly appreciated and helps keep this project alive and updated.

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-orange.svg?style=for-the-badge&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/alaschgari)

## Disclaimer

This integration is an **unofficial** project and is **not** affiliated, associated, authorized, endorsed by, or in any way officially connected with CoinMarketCap, or any of its subsidiaries or its affiliates. The official CoinMarketCap website can be found at [https://coinmarketcap.com](https://coinmarketcap.com).

This project is provided "as is" by a private individual for educational and personal use only. **No warranty** of any kind, express or implied, is made regarding the accuracy, reliability, or availability of this integration. Use it at your own risk. The author assumes no responsibility or liability for any errors or omissions in the content of this project or for any damages arising from its use.
