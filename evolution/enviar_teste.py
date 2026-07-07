import requests
import json

# Configurações de Acesso
URL = "http://localhost:8080/message/sendText/MotorPablo"
API_KEY = "pablito123"

# --- CONFIGURAÇÃO DO SEU NÚMERO ---
NUMERO_DESTINO = "5581992717833" 
# -----------------------------

def enviar_mensagem(numero, texto):
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "number": numero,
        "options": {
            "delay": 1200,          # Simula digitação por 1.2 segundos
            "presence": "composing", # Mostra "digitando..." para você
            "linkPreview": False
        },
        "textMessage": {
            "text": texto
        }
    }

    try:
        print(f"🚀 Enviando mensagem de teste para {numero}...")
        response = requests.post(URL, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            print("\n" + "="*40)
            print("✅ SUCESSO ABSOLUTO!")
            print("Verifique seu WhatsApp agora.")
            print("="*40)
        else:
            print(f"❌ ERRO {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ FALHA DE CONEXÃO COM O SERVIDOR: {e}")

if __name__ == "__main__":
    mensagem_teste = (
        "🤖 *Motor Pablo Ativado!*\n\n"
        "Gabriel, este é o sinal verde que precisávamos.\n"
        "Se você recebeu esta mensagem, o robô já está pronto para o próximo passo.\n\n"
        "Status: *Pronto para disparos em massa!* 🚀"
    )
    
    enviar_mensagem(NUMERO_DESTINO, mensagem_teste)