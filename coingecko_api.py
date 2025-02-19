import asyncio
import requests
from indicators.ema import calculate_ema

# Função para obter o preço de um ativo da CoinGecko
async def get_coingecko_price(symbol: str):
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": symbol,
        "vs_currencies": "usd"
    }
    
    response = await asyncio.to_thread(requests.get, url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data[symbol]["usd"]
    else:
        print(f"Erro ao obter preço para {symbol}: {response.status_code} - {response.text}")
        return None

# Função para obter os candles históricos da CoinGecko
async def get_historical_klines(symbol: str, days: int = 365, interval: str = "daily"):
    """
    Obtém os candles históricos para um ativo da CoinGecko.
    
    :param symbol: O símbolo do ativo (ex: "bitcoin").
    :param days: Quantidade de dias a buscar.
    :param interval: Intervalo de tempo (ex: "daily", "hourly").
    :return: Lista de preços de fechamento.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": interval
    }
    
    response = await asyncio.to_thread(requests.get, url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        # Extrair preços de fechamento
        return [float(price[1]) for price in data["prices"]]
    else:
        print(f"Erro ao obter candles para {symbol}: {response.status_code} - {response.text}")
        return []

# Teste: Buscar dados, calcular EMAs e verificar sinal de trade
# if __name__ == "__main__":
#     symbol = "bitcoin"
#     candles = asyncio.run(get_historical_klines(symbol, days=365))  # Pegamos 365 dias de candles

#     if candles:
#         ema_9 = calculate_ema(candles, 9)
#         ema_21 = calculate_ema(candles, 21)

#         signal = check_trade_signal(ema_9, ema_21)

#         print(f"EMA 9: {ema_9}, EMA 21: {ema_21}, Sinal: {signal}")
#     else:
#         print("Não foi possível obter os dados históricos.")
