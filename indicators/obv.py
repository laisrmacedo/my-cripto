import pandas as pd

def calculate_obv(candles):
    """
    Calcula o OBV usando Pandas.

    :param candles: Lista de dicionários contendo "close" e "volume".
    :return: Pandas Series com os valores de OBV.
    """
    df = pd.DataFrame(candles)
    
    df["price_change"] = df["close"].diff()  # Diferença de preço entre os candles
    df["volume_change"] = df["volume"] * df["price_change"].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    df["obv"] = df["volume_change"].cumsum()  # Soma cumulativa do OBV

    return df["obv"]
