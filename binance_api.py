import asyncio
from binance.client import Client
import time
import requests
import aiohttp
import time
import asyncio

async def get_historical_klines(symbol: str, days: int = 365, interval: str = "1d"):
    """
    Obtém os candles históricos para um ativo da Binance, garantindo que retorna os dados mais recentes.
    
    :param symbol: O símbolo do ativo no formato Binance (ex: "BTCUSDT").
    :param days: Quantidade de dias a buscar.
    :param interval: Intervalo de tempo (ex: "1d", "1h", "4h").
    :return: Lista de preços de fechamento.
    """
    url = "https://api.binance.com/api/v3/klines"
    
    # Timestamp atual e início baseado em 'days' atrás
    end_time = int(time.time() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)
    
    all_closes = []
    limit = 1000  # Máximo de candles por requisição permitido pela Binance
    async with aiohttp.ClientSession() as session:
        while True:
            params = {
                "symbol": symbol,
                "interval": interval,
                "startTime": start_time,
                "endTime": end_time,
                "limit": limit
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data:
                        break  # Se não houver mais dados, interrompe o loop
                    
                    # Adiciona os preços de fechamento (posição 4 no array)
                    closes = [float(candle[4]) for candle in data]
                    all_closes.extend(closes)

                    # Atualiza o start_time para continuar de onde parou
                    start_time = int(data[-1][0]) + 1  

                    # Se recebeu menos do que o limite, já pegou tudo
                    if len(closes) < limit:
                        break
                else:
                    print(f"Erro ao obter candles para {symbol}: {response.status} - {await response.text()}")
                    return []
    
    return all_closes[-(days * (24 // int(interval[:-1]))):]  # Garante que retorna apenas os mais recentes


# Inicializar o cliente da Binance (sem precisar de chave de API, pois você só está acessando dados públicos)
client = Client()

async def get_binance_price(symbol: str):
    # Utilizar asyncio.to_thread para executar a função de forma assíncrona
    price = await asyncio.to_thread(client.get_symbol_ticker, symbol=symbol)
    return price['price'] if price else None
