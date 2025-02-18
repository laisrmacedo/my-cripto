import asyncio
from binance.client import Client
from market_data import get_top_200_coins
from indicators.ema import calculate_ema, check_trade_signal


top_coins = get_top_200_coins()

# Inicializar o cliente da Binance (sem precisar de chave de API, pois você só está acessando dados públicos)
client = Client()

async def get_binance_price(symbol: str):
    # Utilizar asyncio.to_thread para executar a função de forma assíncrona
    price = await asyncio.to_thread(client.get_symbol_ticker, symbol=symbol)
    return price['price'] if price else None

async def get_historical_klines(symbol: str, interval: str = "1h", limit: int = 21):
    """
    Obtém os candles históricos para um ativo da Binance.
    
    :param symbol: O símbolo do ativo (ex: "BTCUSDT").
    :param interval: O intervalo do candle (ex: "1h", "4h", "1d").
    :param limit: Quantidade de candles a buscar (mínimo 21 para EMA 21).
    :return: Lista de preços de fechamento.
    """
    klines = await asyncio.to_thread(client.get_klines, symbol=symbol, interval=interval, limit=limit)

    # Retorna apenas os preços de fechamento (posição 4 em cada candle)
    return [float(candle[4]) for candle in klines]

# Teste: Buscar dados, calcular EMAs e verificar sinal de trade
if __name__ == "__main__":
    symbol = "BTCUSDT"
    candles = asyncio.run(get_historical_klines(symbol, limit=21))  # Pegamos 21 candles

    ema_9 = calculate_ema(candles, 9)
    ema_21 = calculate_ema(candles, 21)

    signal = check_trade_signal(ema_9, ema_21)

    print(f"EMA 9: {ema_9}, EMA 21: {ema_21}, Sinal: {signal}")