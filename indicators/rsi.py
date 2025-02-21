import pandas as pd

def calculate_rsi(prices, period=14):
    """
    Calcula o Índice de Força Relativa (RSI) usando SMA, compatível com o TradingView.
    
    O cálculo do RSI deve ser feito apenas com preços de fechamento de candles fechados.

    :param prices: Lista de preços de fechamento.
    :param period: Período do RSI (padrão: 14).
    :return: Último valor do RSI calculado.
    """
    if len(prices) < period + 1:  # Precisa de pelo menos (período + 1) preços para iniciar corretamente
        return None

    # Considera apenas os preços fechados, ou seja, ignora o último preço não fechado
    df = pd.DataFrame(prices[:-1], columns=["close"])

    df["return"] = df["close"].diff()

    df["gain"] = df["return"].apply(lambda x: x if x > 0 else 0)
    df["loss"] = df["return"].apply(lambda x: -x if x < 0 else 0)

    # Passo 1: Calcular o primeiro valor da média móvel simples (SMA)
    first_avg_gain = df["gain"].iloc[1:period+1].mean()
    first_avg_loss = df["loss"].iloc[1:period+1].mean()

    # Criar listas para armazenar os valores médios de ganho e perda
    avg_gains = [first_avg_gain]
    avg_losses = [first_avg_loss]

    # Passo 2: Aplicar a média móvel simples (SMA) para os próximos valores
    for i in range(period+1, len(df)):
        gain = df["gain"].iloc[i]
        loss = df["loss"].iloc[i]

        # Calculando a média simples
        new_avg_gain = (avg_gains[-1] * (period - 1) + gain) / period
        new_avg_loss = (avg_losses[-1] * (period - 1) + loss) / period

        avg_gains.append(new_avg_gain)
        avg_losses.append(new_avg_loss)

    # Adiciona os valores calculados ao DataFrame
    df.loc[period:, "avg_gain"] = avg_gains
    df.loc[period:, "avg_loss"] = avg_losses

    # Calcula o RSI
    df["rs"] = df["avg_gain"] / df["avg_loss"]
    df["rsi"] = 100 - (100 / (1 + df["rs"]))

    return df["rsi"].iloc[-1] if not df["rsi"].isna().iloc[-1] else None
