import requests

def get_top_200_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 200,
        "page": 1,
        "sparkline": False
    }
    
    response = requests.get(url, params=params)
    data = response.json()

    return [coin["symbol"].upper() for coin in data]

# Teste
if __name__ == "__main__":
    print(get_top_200_coins()[:10])  # Mostra os 10 primeiros
