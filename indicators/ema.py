import pandas as pd

def calculate_ema(prices, period=9):
    df = pd.DataFrame(prices, columns=["close"])
    df[f"ema_{period}"] = df["close"].ewm(span=period, adjust=False).mean()
    return df[f"ema_{period}"].iloc[-1]

def calculate_sma(prices, period=200):
    df = pd.DataFrame(prices, columns=["close"])
    df[f"sma_{period}"] = df["close"].rolling(window=period).mean()
    return df[f"sma_{period}"].iloc[-1] if len(df) >= period else None  # Retorna a última SMA se houver dados suficientes