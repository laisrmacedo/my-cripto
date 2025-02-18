import requests
import os
from dotenv import load_dotenv

load_dotenv()  
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_test_message():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": "✅ Teste: Mensagem enviada com sucesso!"}
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("✅ Mensagem enviada com sucesso!")
    else:
        print(f"❌ Erro ao enviar mensagem: {response.text}")

# Executa o teste
send_test_message()
