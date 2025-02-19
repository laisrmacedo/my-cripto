import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Bot
from indicators.ema import calculate_ema, calculate_sma
from indicators.check_trade_signal import check_trade_signal
from indicators.rsi import calculate_rsi
from indicators.macd import calculate_macd
from market_data import get_top_30_coins
# from coingecko_api import get_coingecko_price, get_historical_klines  # CoinGecko API
from binance_api import get_binance_price, get_historical_klines  # Binance API
from flask import Flask
import threading
import time

# Configuração do logging
logging.basicConfig(level=logging.INFO)

# Carregar variáveis de ambiente
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Inicializar o bot do Telegram
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Inicializar o servidor Flask
app = Flask(__name__)

async def check_market_signals():
    """
    Verifica sinais de compra/venda usando EMAs, RSI e MACD e envia alertas no Telegram.
    """
    top_coins = get_top_30_coins()
    messages = []

    # COINGECKO API
    # for symbol in top_coins["coingecko"]:
    # BINANCE API
    for symbol in top_coins["binance"]:
        try:
            # COINGECKO API
            # candles = await get_historical_klines(symbol, days=365)
            # print(candles)
            
            # BINANCE API
            candles = await get_historical_klines(symbol, days=365, interval="1d")
            if not candles:
                continue

            # Calcular indicadores
            ema_9 = calculate_ema(candles, 9)
            ema_21 = calculate_ema(candles, 21)
            ema_50 = calculate_ema(candles, 50)
            ema_200 = calculate_ema(candles, 200)
            sma_200 = calculate_sma(candles, 200)
            rsi = calculate_rsi(candles)
            macd, signal_line = calculate_macd(candles)

            price = candles[-1]  # Último preço de fechamento
            ema_signal = check_trade_signal(ema_9, ema_21, ema_50, ema_200, sma_200, price)

            # Condições para sinais completos de COMPRA
            if any("tendência de alta" in s for s in ema_signal) and price > sma_200 and rsi < 30 and macd > signal_line:
                message = (f"📢 {symbol} sinalizou **COMPRA FORTE**!\n"
                        f"- {ema_signal}\n"
                        f"- RSI: {rsi:.2f} (sobrevendido)\n"
                        f"- MACD: {macd:.2f} cruzando acima da linha de sinal\n"
                        f"- Preço acima da SMA 200 ➝ Confirmação de tendência de alta ✅")
                messages.append(message)

            # Condições para sinais completos de VENDA
            elif any("tendência de baixa" in s for s in ema_signal) and price < sma_200 and rsi > 70 and macd < signal_line:
                message = (f"📢 {symbol} sinalizou **VENDA FORTE**!\n"
                        f"- {ema_signal}\n"
                        f"- RSI: {rsi:.2f} (sobrecomprado)\n"
                        f"- MACD: {macd:.2f} cruzando abaixo da linha de sinal\n"
                        f"- Preço abaixo da SMA 200 ➝ Confirmação de tendência de baixa 🔻")
                messages.append(message)

        except Exception as e:
            logging.error(f"Erro ao processar {symbol}: {e}")

    if messages:
        final_message = "\n\n".join(messages)
    else:
        final_message = "📢 Nenhum sinal forte encontrado no momento."
        print(final_message)

    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=final_message, parse_mode="Markdown")

# Agendar verificação de sinais
# if __name__ == "__main__":
#     asyncio.run(check_market_signals())

def run_flask():
    """
    Função para rodar o servidor Flask.
    """
    app.run(host='0.0.0.0', port=10000)

def schedule_check():
    """
    Função para rodar a verificação de sinais de 5 em 5 minutos.
    """
    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(check_market_signals())  # Executa o bot
        time.sleep(5 * 60)  # Espera 5 minutos antes de rodar novamente

# Roda o servidor Flask em uma thread separada
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Roda a verificação dos sinais a cada 5 minutos
schedule_check()
