import requests

url = "http://127.0.0.1:8080/instance/create"
payload = {
    "instanceName": "MotorPablo",
    "qrcode": True
}
# A chave atualizada com a senha do seu servidor
headers = {
    "Content-Type": "application/json",
    "apikey": "pablito123" 
}

print("⚙️ Registrando o Motor Pablo no sistema novo...")
try:
    resposta = requests.post(url, json=payload, headers=headers)
    
    if resposta.status_code in [200, 201]:
        print("✅ Instância criada com sucesso! A amnésia acabou.")
        print("➡️  Agora você já pode rodar o 'python novo_qr.py' normalmente.")
    else:
        print(f"❌ Erro ao criar: {resposta.text}")
except Exception as e:
    print(f"❌ Erro de conexão: {e}")