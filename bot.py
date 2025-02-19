import os
from dotenv import load_dotenv
import nest_asyncio
import asyncio
import logging
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler
from indicators.ema import calculate_ema, check_trade_signal
from datetime import datetime, timedelta
from coingecko_api import get_coingecko_price, get_historical_klines  # Alterado para CoinGecko API
from market_data import get_top_30_coins
from tests.test_telegram import send_test_message

# Configuração do logging para depuração
logging.basicConfig(level=logging.INFO)

# Carregar variáveis de ambiente
load_dotenv()  
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Inicializar o bot do Telegram
bot = Bot(token=TELEGRAM_BOT_TOKEN)
nest_asyncio.apply()

# Função de resposta para o comando /price
async def price(update: Update, context):
    if context.args:
        symbol = context.args[0]  # Primeiro argumento após o comando /price
        price = await get_coingecko_price(symbol)  # Alterado para CoinGecko
        if price:
            await update.message.reply_text(f'O preço de {symbol} é {price} USD')
        else:
            await update.message.reply_text(f'Não foi possível obter o preço para {symbol}')
    else:
        await update.message.reply_text("Por favor, forneça um símbolo de token após o comando. Exemplo: /price bitcoin")

# Função para iniciar o bot
async def start(update: Update, context):
    await update.message.reply_text("Olá, sou seu bot!")

# Função principal para iniciar o bot
async def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Adicionar handlers para comandos
    start_handler = CommandHandler('start', start)
    price_handler = CommandHandler('price', price)
    application.add_handler(start_handler)
    application.add_handler(price_handler)

    # Iniciar o bot com polling
    await application.run_polling()

# Função que verifica os sinais de compra/venda para os 200 ativos
async def check_market_signals():
    """
    Verifica os sinais de compra/venda para os 200 ativos com maior market cap e envia alertas no Telegram.
    """
    top_coins = get_top_30_coins()  # Buscar os 30 ativos com maior market cap
    messages = []

    for symbol in top_coins:
        try:
            candles = await get_historical_klines(symbol, days=365) 

            if candles:
                ema_9 = calculate_ema(candles, 9)
                ema_21 = calculate_ema(candles, 21)
                signal = check_trade_signal(ema_9, ema_21)

                if signal:
                    message = f"📢 {symbol} sinalizou **{signal.upper()}**!\nEMA 9: {ema_9:.2f}\nEMA 21: {ema_21:.2f}"
                    messages.append(message)

        except Exception as e:
            logging.error(f"Erro ao processar {symbol}: {e}")

    # Enviar alertas se houver sinais
    if messages:
        final_message = "\n\n".join(messages)
    else:
        final_message = "📢 Nenhum sinal encontrado nos últimos 10 minutos."

    # Enviar mensagem no Telegram
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=final_message, parse_mode="Markdown")

# Iniciar o bot e agendar checagem dos sinais
if __name__ == "__main__":
    # Iniciar o bot
    # asyncio.run(main())

    # Agendar checagem dos sinais de mercado a cada intervalo
    asyncio.run(check_market_signals())

    send_test_message()
