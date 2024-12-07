import asyncio
import aiohttp
from datetime import datetime

# Your CoinMarketCap API key (replace with your actual key)
API_KEY = "8e3d4b58-4c9b-4cec-891b-e74a1dc0e285"

# List of cryptocurrency symbols to fetch
SYMBOLS = ["BTC", "ETH", "BNB", "ADA", "XRP"]

# CoinMarketCap API endpoint
COINMARKETCAP_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

async def fetch_price(session, symbol):
    """Fetch the price of a single cryptocurrency symbol."""
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }
    params = {"symbol": symbol}
    
    try:
        async with session.get(COINMARKETCAP_URL, headers=headers, params=params) as response:
            data = await response.json()
            if response.status == 200:
                price = data["data"][symbol]["quote"]["USD"]["price"]
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {symbol}: ${price:,.2f}")
            else:
                print(f"Error fetching {symbol}: {data.get('status', {}).get('error_message', 'Unknown error')}")
    except Exception as e:
        print(f"Exception while fetching {symbol}: {e}")

async def fetch_prices_periodically():
    """Fetch cryptocurrency prices every 10 seconds."""
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = [fetch_price(session, symbol) for symbol in SYMBOLS]
            await asyncio.gather(*tasks)
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(fetch_prices_periodically())
