import pandas as pd

def calculate_macd(candles, short_period=12, long_period=26, signal_period=9):
    """
    Calcula o MACD e a linha de sinal.
    :param prices: Lista de preços de fechamento.
    :param short_period: Período da EMA curta (padrão: 12).
    :param long_period: Período da EMA longa (padrão: 26).
    :param signal_period: Período da linha de sinal (padrão: 9).
    :return: Últimos valores do MACD e da linha de sinal.
    """
    prices = [candle["close"] for candle in candles]
    df = pd.DataFrame(prices, columns=["close"])
    
    df["ema_short"] = df["close"].ewm(span=short_period, adjust=False).mean()
    df["ema_long"] = df["close"].ewm(span=long_period, adjust=False).mean()
    
    df["macd"] = df["ema_short"] - df["ema_long"]  # Linha MACD
    df["signal"] = df["macd"].ewm(span=signal_period, adjust=False).mean()  # Linha de sinal

    return df["macd"].iloc[-2:].tolist(), df["signal"].iloc[-2:].tolist()  # Retorna os últimos dois valores
    
def check_macd_signal(macd_values, signal_values):
    """
    Verifica se houve um cruzamento do MACD com a linha de sinal comparando os dois últimos valores.
    :param macd_values: Lista dos últimos valores do MACD.
    :param signal_values: Lista dos últimos valores da linha de sinal.
    :return: Mensagem de sinal de compra, venda ou None.
    """
    if len(macd_values) < 2 or len(signal_values) < 2:
        return None  # Sem dados suficientes

    macd_prev, macd_now = macd_values[-2], macd_values[-1]
    signal_prev, signal_now = signal_values[-2], signal_values[-1]

    if macd_prev <= signal_prev and macd_now > signal_now:
        return "🟢 COMPRA: MACD cruzou ACIMA da linha de sinal ➝ Tendência de alta"

    elif macd_prev >= signal_prev and macd_now < signal_now:
        return "🔴 VENDA: MACD cruzou ABAIXO da linha de sinal ➝ Tendência de baixa"

    return None  # Nenhum cruzamento detectado
