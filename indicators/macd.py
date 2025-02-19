import pandas as pd

def calculate_macd(prices, short_period=12, long_period=26, signal_period=9):
    """
    Calcula o MACD e a linha de sinal.
    :param prices: Lista de preços de fechamento.
    :param short_period: Período da EMA curta (padrão: 12).
    :param long_period: Período da EMA longa (padrão: 26).
    :param signal_period: Período da linha de sinal (padrão: 9).
    :return: Últimos valores do MACD e da linha de sinal.
    """
    df = pd.DataFrame(prices, columns=["close"])
    
    df["ema_short"] = df["close"].ewm(span=short_period, adjust=False).mean()
    df["ema_long"] = df["close"].ewm(span=long_period, adjust=False).mean()
    
    df["macd"] = df["ema_short"] - df["ema_long"]  # Linha MACD
    df["signal"] = df["macd"].ewm(span=signal_period, adjust=False).mean()  # Linha de sinal

    return df["macd"].iloc[-1], df["signal"].iloc[-1]  # Retorna os últimos valores

def check_macd_signal(macd, signal):
    """
    Verifica se há um sinal de compra ou venda com base no cruzamento do MACD com a linha de sinal.
    :param macd: Último valor do MACD.
    :param signal: Último valor da linha de sinal.
    :return: "compra", "venda" ou None.
    """
    if macd > signal:
        return "COMPRA: MACD cruza acima da linha de sinal ➝ Tendência de alta"
    elif macd < signal:
        return "VENDA: MACD cruza abaixo da linha de sinal ➝ Tendência de baixa"
    return None  # Nenhum sinal
