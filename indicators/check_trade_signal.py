import pandas as pd

def check_trade_signal(ema_9, ema_21, ema_50, ema_200, sma_200, price):
    signals = []
    
    if ema_9 > ema_21 and ema_21 > ema_50:
        signals.append("📈 Curto prazo: Forte tendência de alta (EMA 9 > EMA 21 > EMA 50)")
    elif ema_9 < ema_21 and ema_21 < ema_50:
        signals.append("📉 Curto prazo: Forte tendência de baixa (EMA 9 < EMA 21 < EMA 50)")
    
    if price > sma_200:
        signals.append("✅ Preço acima da SMA 200: Confirmação de tendência de alta")
    else:
        signals.append("❌ Preço abaixo da SMA 200: Confirmação de tendência de baixa")
    
    if ema_9 > ema_50 and ema_50 > ema_200:
        signals.append("🚀 EMA 9 cruzou acima da EMA 50 e ambas acima da EMA 200: Forte tendência de alta!")
    elif ema_9 < ema_50 and ema_50 < ema_200:
        signals.append("⚠️ EMA 9 cruzou abaixo da EMA 50 e ambas abaixo da EMA 200: Forte tendência de baixa!")
    
    if not signals:
        signals.append("🔍 Nenhum padrão claro identificado.")

    return signals
