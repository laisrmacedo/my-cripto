import pandas as pd

def calculate_bollinger_bands(candles, window=20):
    """
    Calcula as Bollinger Bands usando Pandas.

    :param candles: Lista de dicionários contendo "close".
    :param window: O número de períodos para calcular a SMA e o desvio padrão.
    :return: Uma tupla com as bandas superior, média e inferior.
    """
    # Extrair os preços de fechamento dos candles
    closes = [candle["close"] for candle in candles]
    
    # Criar um DataFrame com os preços de fechamento
    df = pd.DataFrame(closes, columns=["close"])
    
    # Calcula a SMA
    df['SMA'] = df['close'].rolling(window=window).mean()
    
    # Calcula o desvio padrão
    df['STD'] = df['close'].rolling(window=window).std()
    
    # Calcula as bandas superior e inferior
    df['upper'] = df['SMA'] + (2 * df['STD'])
    df['lower'] = df['SMA'] - (2 * df['STD'])
    
    return df['upper'].tolist(), df['SMA'].tolist(), df['lower'].tolist()
