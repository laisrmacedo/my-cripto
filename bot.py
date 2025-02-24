import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Application
from indicators.ema import calculate_ema, calculate_sma
from indicators.check_trade_signal import check_media, check_media_sinals
from indicators.rsi import calculate_rsi
from indicators.macd import calculate_macd
from market_data import get_top_50_coins
from binance_api import get_binance_price, get_historical_klines
from flask import Flask
import datetime
from threading import Thread

# Configuração do logging
logging.basicConfig(level=logging.INFO)

# Carregar variáveis de ambiente
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PORT = 5001  # Porta padrão 5000 caso PORT não esteja definida

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

# Lista de tokens observados
observed_tokens = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "LTCUSDT", "ETHBTC", "AAVEUSDT", "SOLUSDT", "HBARUSDT", "ENAUSDT", "CKBUSDT", "FETUSDT", "USUALUSDT", "FLOKIUSDT", "GRTUSDT"]

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
            ema_signal = check_media(ema_9, ema_21, ema_50, ema_200, sma_200, price)

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

    for symbol in observed_tokens:
        try:
            candles = await get_historical_klines(symbol, days=10, interval="4h")
            if not candles:
                continue
            
            price = candles[-1]
            ema_50 = calculate_ema(candles, 50)
            rsi = calculate_rsi(candles)
            previous_rsi = calculate_rsi(candles[:-1])  # RSI do candle anterior

            # RSI Alto
            if rsi > rsi_threshold_high:
                messages.append(f"📢 {symbol} RSI ALTO! RSI: {rsi:.2f}")
            
            # RSI Baixo
            if rsi < rsi_threshold_low:
                messages.append(f"📢 {symbol} RSI BAIXO! RSI: {rsi:.2f}")
            
            # PULLBACK DETECTADO
            previous_price = candles[-2]  # Preço do candle anterior
            if (
                previous_price > ema_50 and  # Preço anterior estava acima da EMA 50
                price <= ema_50 and  # Preço atual tocou a EMA 50 por cima
                previous_rsi < 40 and  # RSI estava abaixo de 40
                rsi > previous_rsi  # RSI está subindo
            ):
                messages.append(f"🎯 {symbol} pode estar finalizando um **PULLBACK**! RSI subindo após tocar a EMA 50.")

        except Exception as e:
            logging.error(f"Erro ao calcular o RSI para {symbol}: {e}")

    final_message = "\n\n".join(messages) if messages else "🫥 Nenhum alerta de RSI."
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=final_message, parse_mode="Markdown")

async def check_ma_alerts():
    """Verifica o EMA e SMA e envia alertas no Telegram."""
    messages = []

    for symbol in observed_tokens:
        try:
            candles_4h = await get_historical_klines(symbol, days=35, interval="4h")
            candles_1d = await get_historical_klines(symbol, days=200, interval="1d")
            if not candles_4h or not candles_1d:
                continue

            ema_9 = calculate_ema(candles_4h, 9)
            ema_21 = calculate_ema(candles_4h, 21)
            ema_50 = calculate_ema(candles_4h, 50)
            ema_200 = calculate_ema(candles_4h, 200)
            sma_200_4h = calculate_sma(candles_4h, 200)
            sma_200_d1 = calculate_sma(candles_1d, 200)

            price = candles_4h[-1]
            ema_signal = check_media_sinals(ema_9, ema_21, ema_50, ema_200, sma_200_4h, sma_200_d1, price)

            # 📌 Formatação da mensagem
            formatted_message = f"📊 *{symbol}* 📊\n" + "\n".join(ema_signal)
            messages.append(formatted_message)

        except Exception as e:
            logging.error(f"Erro ao calcular o MA para {symbol}: {e}")

    # 🔹 Enviar mensagem formatada no Telegram
    final_message = "\n\n".join(messages) if messages else "🫥 Nenhum alerta"
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=final_message, parse_mode="Markdown")

async def main():
    """Executa a verificação de sinais periodicamente."""
    while True:
        await asyncio.gather(
            check_market_signals(),
            check_rsi_alerts()
        )

        logging.info("Aguardando 2 horas para a próxima execução...")
        await asyncio.sleep(60 * 60 * 2)  # 2 horas

async def send_report(update: Update, context: CallbackContext):
    """Executa check_ma_alerts() quando o usuário digitar /report"""
    await check_ma_alerts()
    logging.info("Relatorio enviado.")
    await update.message.reply_text("Relatório finalizado!")

# Criar o bot e adicionar o comando
bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
bot_app.add_handler(CommandHandler("report", send_report))

def run_flask():
    """Inicia o Flask para manter o serviço ativo."""
    app.run(host="0.0.0.0", port=PORT, debug=False)

if __name__ == "__main__":
    # Iniciar o Flask em uma thread separada
    server = Thread(target=run_flask)
    server.start()

    # Iniciar o polling do Telegram em uma thread separada
    # bot_thread = Thread(target=lambda: asyncio.run(bot_app.run_polling()))
    bot_thread = Thread(target=bot_app.run_polling)
    bot_thread.start()

    # Executar a lógica principal de verificação de sinais no loop assíncrono
    asyncio.run(main())
