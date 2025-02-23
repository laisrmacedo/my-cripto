import pandas as pd

def check_media(ema_9, ema_21, ema_50, ema_200, sma_200, price):
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

def check_media_sinals(ema_9, ema_21, ema_50, ema_200, sma_200_4h, sma_200_d1, price):
    short_trend = ""
    medium_trend = ""
    long_trend = ""

    # 🔹 Curto prazo (EMA 9, EMA 21, EMA 50) - sinais rápidos
    if ema_9 > ema_21 > ema_50:
        short_trend = "📈 Curto prazo: Tendência de alta"
    elif ema_9 < ema_21 < ema_50:
        short_trend = "📉 Curto prazo: Tendência de baixa"

    # 🔹 Médio prazo (EMA 50, EMA 200 e SMA 200 no 4h)
    if ema_9 > ema_50 and ema_50 > ema_200:
        medium_trend = "👌🏼 Médio prazo: Forte tendência de alta (EMA 9 > EMA 50 > EMA 200)"
    elif ema_9 < ema_50 and ema_50 < ema_200:
        medium_trend = "⚠️ Médio prazo: Forte tendência de baixa (EMA 9 < EMA 50 < EMA 200)"
    
    # 🔹 Tendência Geral no 4H (SMA 200)
    if price > sma_200_4h:
        medium_trend += " | ✅ Preço acima da SMA 200 (4H): Confirmação de alta no médio prazo"
    else:
        medium_trend += " | ❌ Preço abaixo da SMA 200 (4H): Confirmação de baixa no médio prazo"

    # 🔹 Longo prazo (SMA 200 no D1)
    if price > sma_200_d1:
        long_trend = "🚀 Preço acima da SMA 200 (D1): Tendência de alta no longo prazo"
    else:
        long_trend = "🚨 Preço abaixo da SMA 200 (D1): Tendência de baixa no longo prazo"

    # 🔹 Resumo final  
    signals = [short_trend, medium_trend, long_trend]
    signals = [s for s in signals if s]  # Remove mensagens vazias

    # 🚨 Resolver contradições  
    if "📈 Curto prazo: Tendência de alta" in signals and "⚠️ Médio prazo: Forte tendência de baixa" in signals:
        signals.append("🔄 Sinais mistos: O curto prazo mostra alta, mas o médio prazo está enfraquecendo.")
    
    if "📉 Curto prazo: Tendência de baixa" in signals and "👌🏼 Médio prazo: Forte tendência de alta" in signals:
        signals.append("🔄 Sinais mistos: O curto prazo mostra baixa, mas o médio prazo ainda é positivo.")
    
    if not signals:
        signals.append("🔍 Nenhum padrão claro identificado.")

    return signals
