import requests
import time

URL_WEBHOOK = "http://127.0.0.1:5000/webhook"

def simular_mensagem(texto):
    print(f"\n👤 [CLIENTE FALSO] enviando: '{texto}'")
    
    payload = {
        "key": {
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": False
        },
        "pushName": "Simulador VS Code",
        "message": {
            "conversation": texto
        }
    }
    
    try:
        requests.post(URL_WEBHOOK, json=payload)
        time.sleep(2)
    except Exception as e:
        print(f"❌ Erro ao conectar com o Flask: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE DE ESTRESSE DO MOTOR PABLO")
    print("="*60)
    
    simular_mensagem("Fala, bom dia!")
    simular_mensagem("Queria ver um orçamento para um show do Rafa Cout.")
    simular_mensagem("Vai ser um casamento no dia 20 de dezembro de 2026, no restaurante Amadeu em Recife, às 20h.")
    
    print("\n✅ Disparos concluídos! Olhe o terminal do atendimento para ver a mágica.")