import os
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Recupera a API Key do CoinMarketCap
API_KEY = os.getenv('CMC_API_KEY')

# Função para obter as 200 moedas principais com base no market cap
def get_top_200_coins():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {
        "X-CMC_PRO_API_KEY": API_KEY,
        "Accept": "application/json"
    }
    params = {
        "start": 1,
        "limit": 200,
        "convert": "USD",
        "sort": "market_cap",
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return [coin["symbol"].upper() for coin in data["data"]]
    else:
        print(f"Error: {response.status_code}")
        return []

# Teste
if __name__ == "__main__":
    print(get_top_200_coins()[:10])  # Mostra os 10 primeiros
