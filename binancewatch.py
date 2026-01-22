#!/usr/bin/env python3
"""
BinanceWatch - macOS Menu Bar App
Shows Binance Futures coins with >$1B 24h volume
"""

import rumps
import requests
import threading
from collections import defaultdict

BINANCE_FUTURES_API = "https://fapi.binance.com/fapi/v1/ticker/24hr"
REFRESH_INTERVAL = 60
MIN_VOLUME_BILLION = 1.0


class BinanceWatchApp(rumps.App):
    def __init__(self):
        super().__init__("BinanceWatch", title="₿ ...")
        self.data = []
        self.min_volume = MIN_VOLUME_BILLION

        # Build initial menu
        self.refresh_item = rumps.MenuItem("Refresh Now", callback=self.refresh_now)
        self.vol_menu = rumps.MenuItem("Min Volume")
        self.vol_menu.add(rumps.MenuItem("$250M+", callback=self.set_250m))
        self.vol_menu.add(rumps.MenuItem("$500M+", callback=self.set_500m))
        self.vol_menu.add(rumps.MenuItem("$1B+ (default)", callback=self.set_1b))
        self.vol_menu.add(rumps.MenuItem("$2B+", callback=self.set_2b))
        self.vol_menu.add(rumps.MenuItem("$5B+", callback=self.set_5b))

        # Initial fetch
        self.fetch_data()

        # Start timer for auto-refresh
        self.timer = rumps.Timer(self.timer_callback, REFRESH_INTERVAL)
        self.timer.start()

    def timer_callback(self, _):
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def fetch_data(self):
        try:
            response = requests.get(BINANCE_FUTURES_API, timeout=10)
            response.raise_for_status()
            raw_data = response.json()
            self.data = self.process_data(raw_data)
            self.rebuild_menu()
        except Exception as e:
            print(f"Error: {e}")
            self.title = "₿ !"

    def process_data(self, raw_data):
        coin_data = defaultdict(list)

        for ticker in raw_data:
            symbol = ticker['symbol']

            # Skip delivery/quarterly contracts (they have underscores like BTCUSDT_250328)
            if '_' in symbol:
                continue

            volume_usd = float(ticker['quoteVolume'])
            volume_billions = volume_usd / 1_000_000_000

            if volume_billions < self.min_volume:
                continue

            # Skip extreme volatility (likely delisting/relisting pumps)
            change_pct = abs(float(ticker['priceChangePercent']))
            if change_pct > 150:
                continue

            base_coin = None
            for quote in ['USDT', 'USDC', 'BUSD', 'USD']:
                if symbol.endswith(quote):
                    base_coin = symbol[:-len(quote)]
                    break

            if not base_coin:
                continue

            coin_data[base_coin].append({
                'symbol': symbol,
                'base': base_coin,
                'price': float(ticker['lastPrice']),
                'change_pct': float(ticker['priceChangePercent']),
                'volume_usd': volume_usd,
                'volume_billions': volume_billions,
            })

        result = []
        for base_coin, pairs in coin_data.items():
            best_pair = max(pairs, key=lambda x: x['volume_usd'])
            result.append(best_pair)

        result.sort(key=lambda x: x['volume_usd'], reverse=True)
        return result

    def get_tier_dot(self, volume_billions):
        """Get colored dot based on volume tier"""
        if volume_billions >= 1.0:
            return "🔵"  # Blue: >$1B
        elif volume_billions >= 0.5:
            return "⚪"  # White: $500M-$1B
        else:
            return "🟢"  # Green: $250M-$500M

    def rebuild_menu(self):
        # Update title
        self.title = f"₿ {len(self.data)}"

        # Clear and rebuild entire menu
        self.menu.clear()

        # Add coin items
        if not self.data:
            self.menu.add(rumps.MenuItem("No coins above threshold"))
        else:
            for coin in self.data:
                dot = self.get_tier_dot(coin['volume_billions'])
                change_sign = "+" if coin['change_pct'] >= 0 else ""
                price_str = self.format_price(coin['price'])
                change_str = f"{change_sign}{coin['change_pct']:.1f}%"
                vol_str = f"${coin['volume_billions']:.1f}B"

                # Fixed-width formatting for alignment
                label = f"{dot} {coin['base']:<6}  {price_str:<10}  {change_str:>7}  {vol_str:>6}"

                item = rumps.MenuItem(label, callback=self.make_click_handler(coin))
                self.menu.add(item)

        # Add separator and controls
        self.menu.add(None)
        self.menu.add(self.refresh_item)
        self.menu.add(self.vol_menu)
        self.menu.add(None)
        self.menu.add(rumps.MenuItem("Quit BinanceWatch", callback=rumps.quit_application))

    def make_click_handler(self, coin):
        def handler(_):
            import webbrowser
            url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{coin['symbol']}.P"
            webbrowser.open(url)
        return handler

    def format_price(self, price):
        """Format price - max 8 chars for alignment"""
        if price >= 10000:
            return f"${price:,.0f}"
        elif price >= 1000:
            return f"${price:,.0f}"
        elif price >= 100:
            return f"${price:.1f}"
        elif price >= 10:
            return f"${price:.2f}"
        elif price >= 1:
            return f"${price:.3f}"
        elif price >= 0.1:
            return f"${price:.3f}"
        elif price >= 0.01:
            return f"${price:.4f}"
        else:
            return f"${price:.5f}"

    def refresh_now(self, _):
        self.title = "₿ ..."
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def set_250m(self, _):
        self.min_volume = 0.25
        self.title = "₿ ..."
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def set_500m(self, _):
        self.min_volume = 0.5
        self.title = "₿ ..."
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def set_1b(self, _):
        self.min_volume = 1.0
        self.title = "₿ ..."
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def set_2b(self, _):
        self.min_volume = 2.0
        self.title = "₿ ..."
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def set_5b(self, _):
        self.min_volume = 5.0
        self.title = "₿ ..."
        threading.Thread(target=self.fetch_data, daemon=True).start()


if __name__ == "__main__":
    BinanceWatchApp().run()
