import os
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

# Ler as variáveis
telegram_token = os.getenv("TELEGRAM_TOKEN")
binance_api_key = os.getenv("BINANCE_API_KEY")
binance_secret_key = os.getenv("BINANCE_SECRET_KEY")

print("TELEGRAM_TOKEN:", telegram_token)
print("BINANCE_API_KEY:", binance_api_key)
print("BINANCE_SECRET_KEY:", binance_secret_key)
