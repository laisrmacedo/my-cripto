import asyncio
from binance.client import Client
from indicators.ema import calculate_ema
import time
import requests

# Inicializar o cliente da Binance (sem precisar de chave de API, pois você só está acessando dados públicos)
client = Client()

async def get_binance_price(symbol: str):
    # Utilizar asyncio.to_thread para executar a função de forma assíncrona
    price = await asyncio.to_thread(client.get_symbol_ticker, symbol=symbol)
    return price['price'] if price else None

# Função para obter os candles históricos da Binance
async def get_historical_klines(symbol: str, days: int = 365, interval: str = "1d"):
    """
    Obtém os candles históricos para um ativo da Binance.
    
    :param symbol: O símbolo do ativo no formato Binance (ex: "BTCUSDT").
    :param days: Quantidade de dias a buscar.
    :param interval: Intervalo de tempo (ex: "1d", "1h").
    :return: Lista de preços de fechamento.
    """
    url = "https://api.binance.com/api/v3/klines"
    
    # Timestamp atual e início baseado em 'days' atrás
    end_time = int(time.time() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)
    
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_time,
        "endTime": end_time,
        "limit": 1000  # Limite máximo permitido pela Binance
    }
    
    response = await asyncio.to_thread(requests.get, url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        # Extrair preços de fechamento (posição 4)
        return [float(candle[4]) for candle in data]
    else:
        print(f"Erro ao obter candles para {symbol}: {response.status_code} - {response.text}")
        return []

# Teste
# url = "https://api.binance.com/api/v3/ticker/price"
# response = requests.get(url)

# if response.status_code == 200:
#     print("✅ Binance API está respondendo!")
#     print(response.json()[:50])  # Exibe os 5 primeiros ativos retornados
# else:
#     print(f"❌ Erro ao acessar Binance API: {response.status_code}")

