import requests

# Fazendo uma requisição para pegar o preço do Bitcoin em dólares
response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")

if response.status_code == 200:
    data = response.json()
    print(f"Preço do Bitcoin: ${data['bitcoin']['usd']}")
else:
    print("Erro ao buscar o preço do Bitcoin")
