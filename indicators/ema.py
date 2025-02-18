import pandas as pd

def calculate_ema(prices, period=9):
    """
    Calcula a Média Móvel Exponencial (EMA).
    :param prices: Lista de preços de fechamento.
    :param period: Período da EMA (ex: 9 ou 21).
    :return: Valor da EMA calculada.
    """
    df = pd.DataFrame(prices, columns=["close"])
    df[f"ema_{period}"] = df["close"].ewm(span=period, adjust=False).mean()
    return df[f"ema_{period}"].iloc[-1]  # Retorna o último valor da EMA

def check_trade_signal(ema_9, ema_21):
    """
    Verifica se há um sinal de compra ou venda com base no cruzamento das EMAs.
    :param ema_9: Último valor da EMA 9.
    :param ema_21: Último valor da EMA 21.
    :return: "compra", "venda" ou None.
    """
    if ema_9 > ema_21:
        return "COMPRA: EMA 9 cruza acima da EMA 21 ➝ Tendência de alta"
    elif ema_9 < ema_21:
        return "VENDA: EMA 9 cruza abaixo da EMA 21 ➝ Tendência de baixa"
    return None  # Nenhum sinal
