import talib
import numpy as np

# Criamos um array de preços fictícios para testar
prices = np.array([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], dtype=np.float64)

# Calculamos a média móvel simples (SMA) de 5 períodos
sma = talib.SMA(prices, timeperiod=5)

print("Preços:", prices)
print("SMA (5 períodos):", sma)
