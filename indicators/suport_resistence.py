def support_resistance(candles, lookback=20):
    closes = [candle["close"] for candle in candles]
    
    support = min(closes[-lookback:])
    resistance = max(closes[-lookback:])
    
    return support, resistance