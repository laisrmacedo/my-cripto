# bot_commands.py
import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from indicators.check_trade_signal import check_media_sinals
from indicators.ema import calculate_ema
from indicators.ema import calculate_sma
from binance_api import get_historical_klines

# Configuração do logging
logging.basicConfig(level=logging.INFO)

# Carregar variáveis de ambiente
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def check_ma_alerts():
    """Verifica o EMA e SMA e envia alertas no Telegram."""
    logging.info("Iniciando check_ma_alerts")
    messages = []
    observed_tokens = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

    for symbol in observed_tokens:
        try:
            candles_4h = await get_historical_klines(symbol, days=35, interval="4h")
            candles_1d = await get_historical_klines(symbol, days=200, interval="1d")
            if not candles_4h or not candles_1d:
                logging.warning(f"Sem dados de candles para {symbol}")
                continue

            ema_9 = calculate_ema(candles_4h, 9)
            ema_21 = calculate_ema(candles_4h, 21)
            ema_50 = calculate_ema(candles_4h, 50)
            ema_200 = calculate_ema(candles_4h, 200)
            sma_200_4h = calculate_sma(candles_4h, 200)
            sma_200_d1 = calculate_sma(candles_1d, 200)

            price = candles_4h[-1]
            ema_signal = check_media_sinals(ema_9, ema_21, ema_50, ema_200, sma_200_4h, sma_200_d1, price)

            formatted_message = f"📊 *{symbol}* 📊\n" + "\n".join(ema_signal)
            messages.append(formatted_message)
        except Exception as e:
            logging.error(f"Erro ao calcular o MA para {symbol}: {e}")

    final_message = "\n\n".join(messages) if messages else "🫥 Nenhum alerta"
    return final_message

async def send_report(update: Update, context: CallbackContext):
    """Executa check_ma_alerts() quando o usuário digitar /report"""
    logging.info("Comando /report recebido")
    try:
        message = await check_ma_alerts()
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Erro ao enviar relatório: {e}")
        await update.message.reply_text("Ocorreu um erro ao gerar o relatório.")

if __name__ == "__main__":
    bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("report", send_report))
    bot_app.run_polling()
