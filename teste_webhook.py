import requests
import time

URL_WEBHOOK = "http://localhost:5000/webhook/whatsapp"

# O cliente preenche a última lacuna: o horário.
payload_cliente = {
    "wa_id": "5581988888888",
    "name": "Cliente Novo V8",
    "text": "A festa começa às 20h, e queremos que o Rafa entre às 23h."
}

print(f"🚀 Estresse Contínuo V8 - Mensagem 4 (Triagem Concluída e Gatilho Comercial)...")
inicio = time.time()

try:
    resposta = requests.post(URL_WEBHOOK, json=payload_cliente)
    fim = time.time()
    
    dados_resposta = resposta.json()
    
    print(f"\n✅ Status HTTP: {resposta.status_code}")
    print(f"⏱️ Tempo total (Stealth Mode V8): {fim - inicio:.2f} segundos")
    print(f"📡 Status Interno do Orquestrador: {dados_resposta.get('status')}")
    print(f"🤖 Resposta do Pablo:\n{dados_resposta.get('response')}")
    
except Exception as e:
    print(f"❌ Erro crítico: {e}")