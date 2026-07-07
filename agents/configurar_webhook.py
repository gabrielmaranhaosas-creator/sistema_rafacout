import requests

# Endereço da Evolution API
URL_BASE = "http://localhost:8080"
INSTANCIA = "MotorPablo"
API_KEY = "pablito123"

def ativar_webhook():
    print("🔌 Conectando Evolution API ao Cérebro Flask...")
    
    url = f"{URL_BASE}/webhook/set/{INSTANCIA}"
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Dizemos para a API: "Mande as mensagens recebidas para a porta 5000"
    payload = {
        "webhook": {
            "url": "http://127.0.0.1:5000/webhook",
            "byEvents": False,
            "base64": False,
            "events": [
                "MESSAGES_UPSERT" # Evento de receber nova mensagem
            ]
        }
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code in [200, 201]:
            print("✅ SUCESSO! Webhook configurado.")
            print("🤖 O Motor Pablo agora responde automaticamente!")
        else:
            print(f"❌ Erro: {res.text}")
    except Exception as e:
        print(f"❌ Falha de conexão: {e}")

if __name__ == "__main__":
    ativar_webhook()