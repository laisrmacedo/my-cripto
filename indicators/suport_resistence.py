def calculate_fibonacci_levels(candles):
    """Calcula os níveis de Fibonacci baseado no High e Low recentes."""
    highs = [candle["high"] for candle in candles]
    lows = [candle["low"] for candle in candles]

    high = max(highs)
    low = min(lows)

    diff = high - low
    levels = {
        "23.6%": high - diff * 0.236,
        "38.2%": high - diff * 0.382,
        "50.0%": high - diff * 0.5,
        "61.8%": high - diff * 0.618,
        "78.6%": high - diff * 0.786,
    }
    
    return levels, high, low

def support_resistance(candles, price):
    """Encontra os níveis de suporte e resistência usando máximas/mínimas recentes e Fibonacci."""
    # 📌 Máximas e mínimas recentes
    highs = [candle["high"] for candle in candles[-50:]]  # Últimos 50 candles
    lows = [candle["low"] for candle in candles[-50:]]  # Últimos 50 candles
    
    recent_resistance = max(highs)
    recent_support = min(lows)

    # 📌 Suporte e resistência usando Fibonacci
    fibonacci_levels, fib_high, fib_low = calculate_fibonacci_levels(candles)
    
    fib_support = fib_low  # Valor mínimo como fallback
    fib_resistance = fib_high  # Valor máximo como fallback
    
    for level_price in fibonacci_levels.values():
        if level_price < price:
            fib_support = level_price
        elif level_price > price and fib_resistance == fib_high:
            fib_resistance = level_price

    return {
        "recent_support": recent_support,
        "recent_resistance": recent_resistance,
        "fib_support": fib_support,
        "fib_resistance": fib_resistance,
    }