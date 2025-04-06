import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Application, JobQueue
from indicators.ema import calculate_ema, calculate_sma
from indicators.check_trade_signal import check_media, check_media_sinals
from indicators.rsi import calculate_rsi
from indicators.macd import calculate_macd
from indicators.obv import calculate_obv
from indicators.bollinger_bands import calculate_bollinger_bands
from indicators.suport_resistence import support_resistance
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

# Lista de tokens observados
observed_tokens = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "LTCUSDT", "ETHBTC", "AAVEUSDT", "SOLUSDT", "HBARUSDT", "ENAUSDT", "CKBUSDT", "FETUSDT", "FLOKIUSDT", "GRTUSDT", "IOUSDT", "SAGAUSDT", "RDNTUSDT", "USUALUSDT"]
# observed_tokens = ["ETHBTC"]

async def check_market_signals():
    """Verifica sinais de compra/venda e envia alertas no Telegram."""
    top_coins = get_top_50_coins()
    messages = []
    logging.info("check_market_signals")

    for symbol in top_coins["binance"]:
        try:
            candles = await get_historical_klines(symbol, days=365, interval="1d")
            if not candles:
                logging.warning(f"Sem dados de candles para {symbol}")
                continue

            ema_9 = calculate_ema(candles, 9)
            ema_21 = calculate_ema(candles, 21)
            ema_50 = calculate_ema(candles, 50)
            ema_200 = calculate_ema(candles, 200)
            sma_200 = calculate_sma(candles, 200)
            rsi = calculate_rsi(candles)
            macd, signal_line = calculate_macd(candles)

            price = candles[-1]["close"]
            ema_signal = check_media(ema_9, ema_21, ema_50, ema_200, sma_200, price)

            if any("tendência de alta" in s for s in ema_signal) and rsi < 30 and macd[-2] < signal_line[-2] and macd[-1] > signal_line[-1]:
                messages.append(f"🟢🚨 {symbol} sinalizou **COMPRA FORTE**! RSI: {rsi:.2f}, MACD cruzando acima.")
            
            elif ema_9 > ema_21 and price > sma_200 and rsi < 50 and macd[-2] < signal_line[-2] and macd[-1] > signal_line[-1]:
                messages.append(f"🟢 {symbol} sinalizou **COMPRA**! RSI: {rsi:.2f}, MACD cruzando acima.")
            
            elif any("tendência de baixa" in s for s in ema_signal) and price > sma_200 and rsi > 70 and macd[-2] > signal_line[-2] and macd[-1] < signal_line[-1]:
                messages.append(f"🔴🚨 {symbol} sinalizou **VENDA FORTE**! RSI: {rsi:.2f}, MACD cruzando abaixo.")

            elif ema_9 < ema_21 and price < sma_200 and rsi > 50 and macd[-2] > signal_line[-2] and macd[-1] < signal_line[-1]:
                messages.append(f"🔴 {symbol} sinalizou **VENDA**! RSI: {rsi:.2f}, MACD cruzando abaixo.")
            
        except Exception as e:
            logging.error(f"check_market_signals - Erro ao processar {symbol}: {e}")

    final_message = "\n\n".join(messages) if messages else "👎🏼 Nenhum sinal forte encontrado."
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=final_message, parse_mode="Markdown")
    logging.info("Finalizando check_market_signals")

async def check_rsi_alerts():
    """Verifica o RSI e envia alertas no Telegram caso esteja fora dos limites."""
    messages = []
    rsi_high = 70
    rsi_low = 30
    logging.info("check_rsi_alerts")

    for symbol in observed_tokens:
        try:
            candles_4h = await get_historical_klines(symbol, days=10, interval="4h")
            candles_1d = await get_historical_klines(symbol, days=100, interval="1d")
            if not candles_4h or not candles_1d:
                logging.warning(f"Sem dados de candles para {symbol}")
                continue
            
            price = candles_4h[-1]["close"]
            ema_50 = calculate_ema(candles_4h, 50)
            rsi_4h = calculate_rsi(candles_4h)
            rsi_1d = calculate_rsi(candles_1d)
            previous_rsi_4h = calculate_rsi(candles_4h[:-1])  # RSI do candle anterior

            # RSI 4h Alto
            if rsi_4h > rsi_high:
                messages.append(f"📢 {symbol} RSI 4h ALTO! RSI: {rsi_4h:.2f}")
            
            # RSI 4h Baixo
            if rsi_4h < rsi_low:
                messages.append(f"📢 {symbol} RSI 4h BAIXO! RSI: {rsi_4h:.2f}")

            # RSI 1d Alto
            if rsi_1d > rsi_high:
                messages.append(f"‼️ {symbol} RSI 1D ALTO! RSI: {rsi_1d:.2f}")
            
            # RSI 1d Baixo
            if rsi_1d < rsi_low:
                messages.append(f"‼️ {symbol} RSI 1D BAIXO! RSI: {rsi_1d:.2f}")
            
            # PULLBACK DETECTADO
            previous_price = candles_4h[-2]["close"]  # Preço do candle anterior
            if (
                previous_price > ema_50 and  # Preço anterior estava acima da EMA 50
                price <= ema_50 and  # Preço atual tocou a EMA 50 por cima
                previous_rsi_4h < 40 and  # RSI estava abaixo de 40
                rsi > previous_rsi_4h  # RSI está subindo
            ):
                messages.append(f"🎯 {symbol} pode estar finalizando um **PULLBACK**! RSI subindo após tocar a EMA 50.")

        except Exception as e:
            logging.error(f"Erro ao calcular o RSI para {symbol}: {e}")

    final_message = "\n\n".join(messages) if messages else "🫥 Nenhum alerta de RSI 4h."
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=final_message, parse_mode="Markdown")
    logging.info("Finalizando check_rsi_alerts")

async def check_reversals():
    """Verifica sinais de fundo/topo e envia alertas no Telegram."""
    messages = []
    logging.info("check_reversals")

    for symbol in observed_tokens:
        try:
            candles = await get_historical_klines(symbol, days=100, interval="1d")
            if not candles:
                logging.warning(f"Sem dados para {symbol}")
                continue

            if len(candles) < 22:  # Verifica se há candles suficientes para calcular a média de volume
                logging.warning(f"Dados insuficientes para {symbol}")
                continue

            price = candles[-1]["close"]
            volume = [float(candle["volume"]) for candle in candles[-21:-1]]
            avg_volume = sum(volume) / len(volume) if volume else 0
            latest_volume = float(candles[-1]["volume"])
            rsi = calculate_rsi(candles)
            macd, signal_line = calculate_macd(candles)
            obv = calculate_obv(candles)
            upper_band, sma, lower_band = calculate_bollinger_bands(candles)

            if len(obv) < 3:
                logging.warning(f"Dados insuficientes de OBV para {symbol}")
                continue

            if len(macd) < 2 or len(signal_line) < 2:
                logging.warning(f"Dados insuficientes de MACD para {symbol}")
                continue

            # 🚀 Sinal de Fundo Forte
            if latest_volume > 1.5 * avg_volume and rsi < 30 and macd[-2] < signal_line[-2] and macd[-1] > signal_line[-1] and (macd[-1] - signal_line[-1]) > 0.01 and obv.iloc[-1] > obv.iloc[-3] and price <= lower_band[-1] * 1.02:
                messages.append(f"🟢🚨 {symbol} pode estar em **Fundo**! RSI 1D: {rsi:.2f}, entrada de volume comprador, MACD cruzando acima.")
            
            # 🚨 Sinal de Topo Forte
            elif latest_volume > 1.5 * avg_volume and rsi > 70 and macd[-2] > signal_line[-2] and macd[-1] < signal_line[-1] and (signal_line[-1] - macd[-1]) > 0.01 and obv.iloc[-1] < obv.iloc[-3] and price >= upper_band[-1] * 0.98:
                messages.append(f"🔴🚨 {symbol} pode estar em **Topo**! RSI 1D: {rsi:.2f}, saida de volume comprador, MACD cruzando abaixo.")
            
            # 🟡 Alerta de possível fundo
            elif rsi < 40 and abs(macd[-1] - signal_line[-1]) < 0.02 and macd[-1] > signal_line[-1] and obv.iloc[-1] > obv.iloc[-3] and price < lower_band[-1] * 1.05:
                messages.append(f"🟡📉 {symbol} pode estar se aproximando de um **Fundo**! RSI 1D: {rsi:.2f}, possível cruzamento MACD em breve.")
            
            # 🟡 Alerta de possível topo
            elif rsi > 60 and abs(macd[-1] - signal_line[-1]) < 0.02 and macd[-1] < signal_line[-1] and obv.iloc[-1] < obv.iloc[-3] and price > upper_band[-1] * 0.95:
                messages.append(f"🟡📈 {symbol} pode estar se aproximando de um **Topo**! RSI 1D: {rsi:.2f}, MACD enfraquecendo.")
            
            # 🔵 Confirmação de tendência de alta
            elif rsi > 50 and macd[-2] < signal_line[-2] and macd[-1] > signal_line[-1] and obv.iloc[-1] > obv.iloc[-3]:
                messages.append(f"🟢⬆ {symbol} confirma **tendência de alta**! RSI 1D: {rsi:.2f}, volume comprador crescendo.")
            
            # 🔴 Confirmação de tendência de baixa
            elif rsi < 50 and macd[-2] > signal_line[-2] and macd[-1] < signal_line[-1] and obv.iloc[-1] < obv.iloc[-3]:
                messages.append(f"🔴⬇ {symbol} confirma **tendência de baixa**! RSI 1D: {rsi:.2f}, volume vendedor aumentando.")

        except Exception as e:
            logging.error(f"check_reversals - Erro ao processar {symbol}: {e}")

    final_message = "\n\n".join(messages) if messages else "💤 Nenhum topo/fundo detectado."
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=final_message, parse_mode="Markdown")
    logging.info("Finalizando check_reversals")

async def check_ma_alerts(symbol: str):
    """Verifica o EMA e SMA para um token específico e envia alertas no Telegram."""
    logging.info(f"Iniciando check_ma_alerts para {symbol}")
    
    try:
        candles_4h = await get_historical_klines(symbol, days=35, interval="4h")
        candles_1d = await get_historical_klines(symbol, days=200, interval="1d")
        candles_1w = await get_historical_klines(symbol, days=1400, interval="1w")
        if not candles_4h or not candles_1d or not candles_1w:
            logging.warning(f"Sem dados de candles para {symbol}")
            return f"⚠️ Sem dados disponíveis para {symbol}."

        ema_9 = calculate_ema(candles_4h, 9)
        ema_21 = calculate_ema(candles_4h, 21)
        ema_50 = calculate_ema(candles_4h, 50)
        ema_200 = calculate_ema(candles_4h, 200)
        sma_200_4h = calculate_sma(candles_4h, 200)
        sma_200_d1 = calculate_sma(candles_1d, 200)
        ema_8w = calculate_ema(candles_1w, 8)
        
        price = candles_4h[-1]["close"]
        ema_signal = check_media_sinals(ema_9, ema_21, ema_50, ema_200, sma_200_4h, sma_200_d1, price)
        
        rsi_4h = calculate_rsi(candles_4h)
        rsi_1d = calculate_rsi(candles_1d)
        levels = support_resistance(candles_4h, price)
        
        macd_list, macd_signal_list = calculate_macd(candles_4h)
        macd_current = macd_list[-1]
        macd_previous = macd_list[-2]
        signal_current = macd_signal_list[-1]
        signal_previous = macd_signal_list[-2]

        if macd_current > 0 and macd_previous < signal_previous and macd_current > signal_current:
            macd_trend = "🟢 MACD positivo e cruzando para cima – tendência forte"
        elif macd_current < 0 and macd_previous < signal_previous and macd_current > signal_current:
            macd_trend = "⚠️ MACD negativo, possível reversão"
        elif macd_current > 0 and macd_previous > signal_previous and macd_current < signal_current:
            macd_trend = "🔴 MACD positivo, mas cruzando para baixo – alerta de fraqueza"
        else:
            macd_trend = "⏳ Aguardando sinal..."

        if price < ema_8w:
            price_8w = "⬇ EMA 8s"
        elif price > ema_8w:
            price_8w = "⬆ EMA 8s"

        if price > ema_8w and rsi_1d > 50 and ema_9 > ema_200 and ema_21 > ema_200 and ema_50 > ema_200:
            trend = "🟢 Tendência de alta"
        else:
            trend = "⏳ Aguardando sinal..."

        if rsi_4h > 50 and rsi_1d > 50:
            rsi_trend = "🟢 RSI indica força compradora"
        elif rsi_4h < 50 and rsi_1d < 50:
            rsi_trend = "🔴 RSI indica força vendedora"
        else:
            rsi_trend = "⏳ Aguardando sinal..."

        if rsi_4h < 30 and rsi_1d > 40:
            rsi_signal = "⚪️ RSI 4h sobrevendido, mas RSI 1D saudável – possível oportunidade de compra"
        elif rsi_4h > 70 and rsi_1d < 60:
            rsi_signal = "🟡 RSI 4h sobrecomprado, mas RSI 1D ainda não está alto – alta pode continuar"
        else:
            rsi_signal = "⏳ Aguardando sinal..."

        if abs(levels["recent_support"] - ema_200) < 0.5 * price * 0.01:  # Exemplo: 0.5% de tolerância
            support_confirmation = "🛡️ Suporte próximo da EMA 200 – forte zona de compra"
        elif abs(levels["recent_resistance"] - ema_50) < 0.5 * price * 0.01:
            support_confirmation = "🚀 Resistência próxima da EMA 50 – possível ponto de venda"
        else:
            support_confirmation = "⏳ Suportes e resistências sem confirmação de médias"


        # 📌 Formatação da mensagem
        formatted_message = f"""
        📊 *{symbol}* 📊
        {', '.join(ema_signal)}
        💵 *PREÇO:* {price:.2f} {(price_8w)}
        {(trend)}
        ・ *RSI 4h:* {rsi_4h:.2f} ({'Sobrevendido' if rsi_4h < 30 else 'Sobrecomprado' if rsi_4h > 70 else 'Neutro'})
        ・ *RSI 1d:* {rsi_1d:.2f} ({'⬇ médio prazo' if rsi_1d < 50 else '⬆ médio prazo'})
        {(rsi_trend)}
        {(rsi_signal)}
        {(macd_trend)}
        ・ *Suporte:* {levels['recent_support']:.2f}
        ・ *Resistência:* {levels['recent_resistance']:.2f}
        {(support_confirmation)}
        """

        return formatted_message

    except Exception as e:
        logging.error(f"Erro ao calcular indicadores para {symbol}: {e}")
        return f"❌ Erro ao calcular indicadores para {symbol}."

async def send_report(update: Update, context: CallbackContext):
    """Executa check_ma_alerts() quando o usuário digitar /r <SYMBOL>"""
    logging.info("Comando /r recebido")
    
    # Pegando o símbolo da mensagem do usuário
    try:
        args = context.args  # Lista de argumentos após o comando
        if not args:
            await update.message.reply_text("⚠️ Você precisa informar um símbolo. Exemplo: `/r BTCUSDT`", parse_mode="Markdown")
            return

        symbol = args[0].upper()  # Pegando o primeiro argumento e colocando em maiúsculas
        message = await check_ma_alerts(symbol)
        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Erro ao enviar relatório: {e}")
        await update.message.reply_text("❌ Ocorreu um erro ao gerar o relatório.")
        
async def periodic_check(application: Application):
    """Executa a verificação de sinais periodicamente e envia mensagens."""
    while True:
        await asyncio.gather(
            check_market_signals(),
            check_rsi_alerts(),
            check_reversals()
        )
        
        logging.info("Aguardando 4 horas para a próxima execução...")
        await asyncio.sleep(60 * 60 * 4)

def run_flask():
    """Inicia o Flask para manter o serviço ativo."""
    app.run(host="0.0.0.0", port=PORT, debug=False)

if __name__ == "__main__":
    # Criar a aplicação do Telegram
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Adicionar o comando /r
    application.add_handler(CommandHandler("r", send_report))

    # Iniciar o Flask em uma thread separada
    server = Thread(target=run_flask)
    server.start()

    # Configurando a fila de jobs
    job_queue = application.job_queue
    job_queue.run_once(lambda _: asyncio.create_task(periodic_check(application)), when=0)

    # Rodar o bot normalmente na thread principal
    application.run_polling()
