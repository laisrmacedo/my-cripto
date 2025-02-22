import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Bot
from indicators.ema import calculate_ema, calculate_sma
from indicators.check_trade_signal import check_trade_signal
from indicators.rsi import calculate_rsi
from indicators.macd import calculate_macd
from market_data import get_top_50_coins
from binance_api import get_binance_price, get_historical_klines
from flask import Flask

# Configuração do logging
logging.basicConfig(level=logging.INFO)

# Carregar variáveis de ambiente
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PORT = 5000  # Porta padrão 5000 caso PORT não esteja definida

# Inicializar o bot do Telegram
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Inicializar o servidor Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot está funcionando!"

@app.route('/health_check')
def health_check():
    return "OK", 200

async def check_market_signals():
    """Verifica sinais de compra/venda e envia alertas no Telegram."""
    top_coins = get_top_50_coins()
    messages = []

    for symbol in top_coins["binance"]:
        try:
            candles = await get_historical_klines(symbol, days=365, interval="1d")
            if not candles:
                continue

            ema_9 = calculate_ema(candles, 9)
            ema_21 = calculate_ema(candles, 21)
            ema_50 = calculate_ema(candles, 50)
            ema_200 = calculate_ema(candles, 200)
            sma_200 = calculate_sma(candles, 200)
            rsi = calculate_rsi(candles)
            macd, signal_line = calculate_macd(candles)

            price = candles[-1]
            ema_signal = check_trade_signal(ema_9, ema_21, ema_50, ema_200, sma_200, price)

            if any("tendência de alta" in s for s in ema_signal) and price > sma_200 and rsi < 30 and macd > signal_line:
                messages.append(f"🚨 {symbol} sinalizou **COMPRA FORTE**! RSI: {rsi:.2f}, MACD cruzando acima.")

            elif any("tendência de baixa" in s for s in ema_signal) and price < sma_200 and rsi > 70 and macd < signal_line:
                messages.append(f"🚨 {symbol} sinalizou **VENDA FORTE**! RSI: {rsi:.2f}, MACD cruzando abaixo.")

        except Exception as e:
            logging.error(f"Erro ao processar {symbol}: {e}")

    final_message = "\n\n".join(messages) if messages else "👎🏼 Nenhum sinal forte encontrado."
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=final_message, parse_mode="Markdown")

async def check_rsi_alerts():
    """Verifica o RSI e envia alertas no Telegram caso esteja fora dos limites."""
    messages = []
    rsi_threshold_high = 70
    rsi_threshold_low = 35

    for symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT", "LTCUSDT", "SUIUSDT", "AAVEUSDT", "SOLUSDT"]:
        try:
            candles = await get_historical_klines(symbol, days=10, interval="4h")
            if not candles:
                continue

            rsi = calculate_rsi(candles)

            if rsi > rsi_threshold_high:
                messages.append(f"📢 {symbol} RSI ALTO! RSI: {rsi:.2f} (acima de 70)")
            elif rsi < rsi_threshold_low:
                messages.append(f"📢 {symbol} RSI BAIXO! RSI: {rsi:.2f} (abaixo de 30)")

        except Exception as e:
            logging.error(f"Erro ao calcular o RSI para {symbol}: {e}")

    final_message = "\n\n".join(messages) if messages else "🫥 Nenhum alerta de RSI."
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=final_message, parse_mode="Markdown")


async def main():
    """Executa a verificação de sinais periodicamente."""
    while True:
        await asyncio.gather(
            check_market_signals(),
            check_rsi_alerts()
        )
        logging.info("Aguardando 4 horas para a próxima execução...")
        await asyncio.sleep(10 * 60)  # 4 horas em segundos (14400)

if __name__ == "__main__":
    # Iniciar o Flask em uma thread separada
    from threading import Thread
    server = Thread(target=lambda: app.run(host="0.0.0.0", port=PORT, debug=False))
    server.start()

    # Executar o loop assíncrono principal
    asyncio.run(main())


# async def main():
#     """Executa a verificação de sinais e depois encerra."""
#     await asyncio.gather(
#         check_market_signals(),
#         check_rsi_alerts()
#     )

# if __name__ == "__main__":
#     # Iniciar o Flask
#     from threading import Thread
#     server = Thread(target=lambda: app.run(host="0.0.0.0", port=PORT, debug=False))
#     server.start()

#     # Executar as funções assíncronas
#     asyncio.run(main())



# import os
# import asyncio
# import logging
# from dotenv import load_dotenv
# from telegram import Bot
# from indicators.ema import calculate_ema, calculate_sma
# from indicators.check_trade_signal import check_trade_signal
# from indicators.rsi import calculate_rsi
# from indicators.macd import calculate_macd
# from market_data import get_top_50_coins
# from binance_api import get_binance_price, get_historical_klines
# from flask import Flask
# from threading import Thread


# # Configuração do logging
# logging.basicConfig(level=logging.INFO)


# # Carregar variáveis de ambiente
# load_dotenv()
# TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


# # Inicializar o bot do Telegram
# bot = Bot(token=TELEGRAM_BOT_TOKEN)


# # Inicializar o servidor Flask
# app = Flask(__name__)


# @app.route('/')
# def home():
#    return "Bot está funcionando!"


# async def check_market_signals():
#    """
#    Verifica sinais de compra/venda usando EMAs, RSI e MACD e envia alertas no Telegram.
#    """
#    top_coins = get_top_50_coins()
#    messages = []


#    for symbol in top_coins["binance"]:
#        try:
#            candles = await get_historical_klines(symbol, days=365, interval="1d")
#            if not candles:
#                continue


#            ema_9 = calculate_ema(candles, 9)
#            ema_21 = calculate_ema(candles, 21)
#            ema_50 = calculate_ema(candles, 50)
#            ema_200 = calculate_ema(candles, 200)
#            sma_200 = calculate_sma(candles, 200)
#            rsi = calculate_rsi(candles)
#            macd, signal_line = calculate_macd(candles)


#            price = candles[-1]
#            ema_signal = check_trade_signal(ema_9, ema_21, ema_50, ema_200, sma_200, price)


#            if any("tendência de alta" in s for s in ema_signal) and price > sma_200 and rsi < 30 and macd > signal_line:
#                message = (f"🚨 {symbol} sinalizou **COMPRA FORTE**!\n"
#                           f"- {ema_signal}\n"
#                           f"- RSI: {rsi:.2f} (sobrevendido)\n"
#                           f"- MACD: {macd:.2f} cruzando acima da linha de sinal\n"
#                           f"- Preço acima da SMA 200 ✅")
#                messages.append(message)


#            elif any("tendência de baixa" in s for s in ema_signal) and price < sma_200 and rsi > 70 and macd < signal_line:
#                message = (f"🚨 {symbol} sinalizou **VENDA FORTE**!\n"
#                           f"- {ema_signal}\n"
#                           f"- RSI: {rsi:.2f} (sobrecomprado)\n"
#                           f"- MACD: {macd:.2f} cruzando abaixo da linha de sinal\n"
#                           f"- Preço abaixo da SMA 200 🔻")
#                messages.append(message)


#        except Exception as e:
#            logging.error(f"Erro ao processar {symbol}: {e}")


#    final_message = "\n\n".join(messages) if messages else "👎🏼 Nenhum sinal forte encontrado."
#    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=final_message, parse_mode="Markdown")


# async def check_rsi_alerts():
#    """
#    Verifica o RSI de tokens definidos e envia alertas no Telegram caso o RSI seja acima de 70 ou abaixo de 30.
#    """
#    messages = []
#    rsi_threshold_high = 70
#    rsi_threshold_low = 35


# #    for symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT", "LTCUSDT"]:
#    for symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT", "LTCUSDT", "ETHBTC", "SUIUSDT", "AAVEUSDT", "SOLUSDT", "HBARUSDT", "ENAUSDT", "CKBUSDT", "FETUSDT", "USUALUSDT", "FLOKIUSDT", "GRTUSDT"]:
#        try:
#            candles = await get_historical_klines(symbol, days=10, interval="4h")
#            if not candles:
#                continue

#         #    print(candles)
#            rsi = calculate_rsi(candles)
#         #    print(rsi)

#            if rsi > rsi_threshold_high:
#                messages.append(f"📢 {symbol} sinalizou **RSI ALTO**! RSI: {rsi:.2f} (acima de 70)")
#            elif rsi < rsi_threshold_low:
#                messages.append(f"📢 {symbol} sinalizou **RSI BAIXO**! RSI: {rsi:.2f} (abaixo de 30)")


#        except Exception as e:
#            logging.error(f"Erro ao calcular o RSI para {symbol}: {e}")


#    final_message = "\n\n".join(messages) if messages else "🫥 Nenhum alerta de RSI."
#    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=final_message, parse_mode="Markdown")


# def run_flask():
#    """ Roda o servidor Flask. """
#    app.run(host='0.0.0.0', port=10000)


# async def schedule_check():
#    while True:
#        await asyncio.gather(
#            check_market_signals(),
#            check_rsi_alerts()
#        )
#        await asyncio.sleep(20 * 60)


# def start_schedule():
#    """ Inicia o `schedule_check` dentro de um loop de eventos em uma thread. """
#    loop = asyncio.new_event_loop()
#    asyncio.set_event_loop(loop)
#    loop.run_until_complete(schedule_check())


# if __name__ == "__main__":
#    # Iniciar o Flask em uma thread separada
#    flask_thread = Thread(target=run_flask, daemon=True)
#    flask_thread.start()


#    # Iniciar a verificação de sinais em outra thread
#    check_thread = Thread(target=start_schedule, daemon=True)
#    check_thread.start()


#    # Manter o script rodando
#    flask_thread.join()
#    check_thread.join()


