from binance.client import Client

# Criamos um cliente sem chave de API (somente para leitura pública)
client = Client()

# Pegamos o preço atual do Bitcoin (BTC/USDT)
price = client.get_symbol_ticker(symbol="BTCUSDT")

print(f"Preço do BTC/USDT: {price['price']}")
