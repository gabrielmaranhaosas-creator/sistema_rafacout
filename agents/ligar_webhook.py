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
    
    # A raiz do payload agora contém o "url" exatamente como a API exige
    payload = {
        "url": "http://127.0.0.1:5000/webhook",
        "webhookByEvents": False,
        "webhookBase64": False,
        "events": [
            "MESSAGES_UPSERT"
        ]
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code in [200, 201]:
            print("\n✅ SUCESSO ABSOLUTO! Webhook configurado.")
            print("🤖 O Motor Pablo agora escuta a porta 5000 e responde automaticamente!")
        else:
            print(f"\n❌ Erro {res.status_code}: {res.text}")
    except Exception as e:
        print(f"\n❌ Falha de conexão: {e}")

if __name__ == "__main__":
    ativar_webhook()