from api import CoinGeckoAPI

cg = CoinGeckoAPI()

response = cg.get_price(ids="bitcoin", vs_currencies="usd")
print(response)
