import pandas as pd

def calculate_rsi(prices, period=14):
    """
    Calcula o Índice de Força Relativa (RSI).
    :param prices: Lista de preços de fechamento.
    :param period: Período do RSI (padrão: 14).
    :return: Último valor do RSI calculado.
    """
    df = pd.DataFrame(prices, columns=["close"])
    df["return"] = df["close"].diff()  # Diferença entre os preços

    df["gain"] = df["return"].apply(lambda x: x if x > 0 else 0)  # Apenas ganhos
    df["loss"] = df["return"].apply(lambda x: -x if x < 0 else 0)  # Apenas perdas

    avg_gain = df["gain"].rolling(window=period, min_periods=1).mean()
    avg_loss = df["loss"].rolling(window=period, min_periods=1).mean()

    rs = avg_gain / (avg_loss + 1e-10)  # Evita divisão por zero
    df["rsi"] = 100 - (100 / (1 + rs))

    return df["rsi"].iloc[-1]  # Retorna o último valor do RSI

def check_rsi_signal(rsi, overbought=70, oversold=30):
    """
    Verifica se há um sinal de compra ou venda com base no RSI.
    :param rsi: Último valor do RSI.
    :param overbought: Nível de sobrecompra (padrão: 70).
    :param oversold: Nível de sobrevenda (padrão: 30).
    :return: "compra", "venda" ou None.
    """
    if rsi > overbought:
        return "VENDA: RSI acima de 70 ➝ Mercado sobrecomprado"
    elif rsi < oversold:
        return "COMPRA: RSI abaixo de 30 ➝ Mercado sobrevendido"
    return None  # Nenhum sinal
