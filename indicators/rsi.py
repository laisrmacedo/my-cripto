import pandas as pd

def calculate_rsi(prices, period=14):
    """
    Calcula o Índice de Força Relativa (RSI) usando média móvel simples (SMA),
    mais alinhado com a metodologia padrão do TradingView.
    
    :param prices: Lista de preços de fechamento.
    :param period: Período do RSI (padrão: 14).
    :return: Último valor do RSI calculado.
    """
    if len(prices) < period:
        return None  # Retorna None se não houver dados suficientes
    
    df = pd.DataFrame(prices, columns=["close"])
    df["return"] = df["close"].diff()

    df["gain"] = df["return"].apply(lambda x: x if x > 0 else 0)
    df["loss"] = df["return"].apply(lambda x: -x if x < 0 else 0)

    # Usando SMA em vez de EMA para ser mais preciso em relação ao TradingView
    avg_gain = df["gain"].rolling(window=period).mean()
    avg_loss = df["loss"].rolling(window=period).mean()

    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    return df["rsi"].iloc[-1] if not df["rsi"].isna().iloc[-1] else None
