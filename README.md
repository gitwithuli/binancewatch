# BinanceWatch

A minimal macOS menu bar app that shows Binance Futures coins with high 24h trading volume.

![BinanceWatch Screenshot](screenshot.png)

## Features

- Shows coins with >$1B 24h volume (configurable)
- **Deduplicates** - Only shows one entry per coin (highest volume pair)
- Live data from Binance Futures API
- Auto-refreshes every 60 seconds
- Click any coin to open TradingView chart
- Volume tier indicators (🟢)
- Configurable volume threshold ($500M, $1B, $2B, $5B)

## Install via Homebrew

```bash
brew tap gitwithuli/tap
brew install --cask binancewatch
```

## Manual Install

1. Download `BinanceWatch.zip` from [Releases](https://github.com/gitwithuli/binancewatch/releases)
2. Unzip and move `BinanceWatch.app` to Applications
3. Right-click → Open (first time only, to bypass Gatekeeper)

## Build from Source

```bash
git clone https://github.com/gitwithuli/binancewatch.git
cd binancewatch
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller

# Run directly
python binancewatch.py

# Or build standalone app
pyinstaller BinanceWatch.spec
# App will be in dist/BinanceWatch.app
```

## Usage

- **Menu bar** shows `₿ N` where N is the count of high-volume coins
- **Click** the icon to see the list with prices and 24h changes
- **Click a coin** to open its TradingView chart
- **Settings > Min Volume** to change the threshold
- **Refresh Now** to manually update

## Data Source

Live data from [Binance Futures API](https://binance-docs.github.io/apidocs/futures/en/).

Only USDT perpetual futures are shown. When multiple pairs exist for the same coin (e.g., BTCUSDT, BTCUSDC), only the highest volume pair is displayed.

## License

MIT
