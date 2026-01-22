#!/usr/bin/env python3
"""
BinanceWatch - macOS Menu Bar App
Shows Binance Futures coins with >$1B 24h volume
"""

import rumps
import requests
import threading
import time
from collections import defaultdict

BINANCE_FUTURES_API = "https://fapi.binance.com/fapi/v1/ticker/24hr"
REFRESH_INTERVAL = 60  # seconds
MIN_VOLUME_BILLION = 1.0


class BinanceWatchApp(rumps.App):
    def __init__(self):
        super().__init__("BinanceWatch", title="₿ --")
        self.data = []
        self.min_volume = MIN_VOLUME_BILLION

        # Menu items
        self.settings_menu = rumps.MenuItem("Min Volume")
        self.settings_menu.add(rumps.MenuItem("$500M+", callback=self.set_500m))
        self.settings_menu.add(rumps.MenuItem("$1B+ (default)", callback=self.set_1b))
        self.settings_menu.add(rumps.MenuItem("$2B+", callback=self.set_2b))
        self.settings_menu.add(rumps.MenuItem("$5B+", callback=self.set_5b))

        self.menu = [
            rumps.MenuItem("Loading...", callback=None),
            None,  # Separator
            rumps.MenuItem("Refresh Now", callback=self.manual_refresh),
            self.settings_menu,
            None,
        ]

        # Start background refresh
        self.start_refresh_thread()

    def start_refresh_thread(self):
        """Start background thread for data refresh"""
        def refresh_loop():
            while True:
                try:
                    self.fetch_and_update()
                except Exception as e:
                    print(f"Error fetching data: {e}")
                time.sleep(REFRESH_INTERVAL)

        thread = threading.Thread(target=refresh_loop, daemon=True)
        thread.start()

    def fetch_and_update(self):
        """Fetch data from Binance and update menu"""
        try:
            response = requests.get(BINANCE_FUTURES_API, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Process and filter data
            self.data = self.process_data(data)

            # Update menu on main thread
            rumps.Timer(0, lambda _: self.update_menu()).start()

        except Exception as e:
            print(f"Fetch error: {e}")

    def process_data(self, raw_data):
        """Filter >$1B volume, dedupe by base coin, sort by volume"""
        # Group by base coin
        coin_data = defaultdict(list)

        for ticker in raw_data:
            symbol = ticker['symbol']
            volume_usd = float(ticker['quoteVolume'])
            volume_billions = volume_usd / 1_000_000_000

            # Skip if below threshold
            if volume_billions < self.min_volume:
                continue

            # Extract base coin (remove USDT, USDC, etc.)
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

        # Keep only highest volume pair per coin
        result = []
        for base_coin, pairs in coin_data.items():
            best_pair = max(pairs, key=lambda x: x['volume_usd'])
            result.append(best_pair)

        # Sort by volume descending
        result.sort(key=lambda x: x['volume_usd'], reverse=True)

        return result

    def update_menu(self):
        """Update the menu bar display"""
        # Update title with count
        count = len(self.data)
        if count > 0:
            self.title = f"₿ {count}"
        else:
            self.title = "₿ 0"

        # Clear existing coin items (keep settings)
        keys_to_remove = []
        for key in self.menu.keys():
            if isinstance(key, str) and (key.startswith("🟢") or key.startswith("Loading") or key.startswith("No coins")):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            try:
                del self.menu[key]
            except:
                pass

        # Build new menu items
        if not self.data:
            self.menu.insert_before("Refresh Now", rumps.MenuItem("No coins above threshold", callback=None))
        else:
            for coin in reversed(self.data):  # Reverse so highest volume ends up at top
                change_sign = "+" if coin['change_pct'] >= 0 else ""
                price_str = self.format_price(coin['price'])
                vol_str = f"${coin['volume_billions']:.1f}B"

                label = f"🟢 {coin['base']:6} {price_str:>10}  {change_sign}{coin['change_pct']:.1f}%  {vol_str}"

                item = rumps.MenuItem(label, callback=self.open_tradingview)
                item.coin_data = coin
                self.menu.insert_before("Refresh Now", item)

    def format_price(self, price):
        """Format price based on magnitude"""
        if price >= 10000:
            return f"${price:,.0f}"
        elif price >= 1000:
            return f"${price:,.1f}"
        elif price >= 1:
            return f"${price:.2f}"
        elif price >= 0.01:
            return f"${price:.4f}"
        else:
            return f"${price:.6f}"

    def open_tradingview(self, sender):
        """Open TradingView chart for clicked coin"""
        import webbrowser
        if hasattr(sender, 'coin_data'):
            symbol = sender.coin_data['symbol']
            url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}.P"
            webbrowser.open(url)

    def manual_refresh(self, _):
        """Manual refresh triggered by menu"""
        self.title = "₿ ..."
        threading.Thread(target=self.fetch_and_update, daemon=True).start()

    def set_500m(self, _):
        self.min_volume = 0.5
        self.manual_refresh(None)
        rumps.notification("BinanceWatch", "Volume filter changed", "Now showing coins with >$500M volume")

    def set_1b(self, _):
        self.min_volume = 1.0
        self.manual_refresh(None)
        rumps.notification("BinanceWatch", "Volume filter changed", "Now showing coins with >$1B volume")

    def set_2b(self, _):
        self.min_volume = 2.0
        self.manual_refresh(None)
        rumps.notification("BinanceWatch", "Volume filter changed", "Now showing coins with >$2B volume")

    def set_5b(self, _):
        self.min_volume = 5.0
        self.manual_refresh(None)
        rumps.notification("BinanceWatch", "Volume filter changed", "Now showing coins with >$5B volume")


if __name__ == "__main__":
    BinanceWatchApp().run()
