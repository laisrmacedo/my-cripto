import pandas as pd
from binance_api import get_historical_klines


def calculate_rsi(prices, period=14):
    """
    Calcula o Índice de Força Relativa (RSI).
    
    :param prices: Lista de preços de fechamento.
    :param period: Período do RSI (padrão: 14).
    :return: Último valor do RSI calculado.
    """
    df = pd.DataFrame(prices, columns=["close"])
    df["return"] = df["close"].diff()

    df["gain"] = df["return"].apply(lambda x: x if x > 0 else 0)
    df["loss"] = df["return"].apply(lambda x: -x if x < 0 else 0)

    # Usando média móvel exponencial (EMA) em vez de SMA para suavizar os valores
    avg_gain = df["gain"].ewm(span=period, adjust=False).mean()
    avg_loss = df["loss"].ewm(span=period, adjust=False).mean()

    rs = avg_gain / (avg_loss + 1e-10)  # Pequeno ajuste para evitar divisão por zero
    df["rsi"] = 100 - (100 / (1 + rs))

    return df["rsi"].iloc[-1]  # Retorna o último valor do RSI
