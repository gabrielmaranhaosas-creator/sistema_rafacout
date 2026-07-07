import requests
import base64
import time
import os

URL_BASE = "http://localhost:8080"
HEADERS = {
    "apikey": "pablito123",
    "Content-Type": "application/json"
}
INSTANCIA = "MotorPablo"

nome_imagem = "qrcode_motor_pablo.png"
if os.path.exists(nome_imagem):
    try:
        os.remove(nome_imagem)
    except:
        pass

print("💥 Limpando resquícios da API...")
try:
    requests.delete(f"{URL_BASE}/instance/delete/{INSTANCIA}", headers=HEADERS)
except:
    pass

time.sleep(2)

print("🚀 Gerando QR Code novo...")
PAYLOAD = {
    "instanceName": INSTANCIA,
    "token": "token_secreto_pablo_123",
    "qrcode": True
}

try:
    res = requests.post(f"{URL_BASE}/instance/create", json=PAYLOAD, headers=HEADERS)
    
    if res.status_code in [200, 201]:
        data = res.json()
        qr_b64 = data["qrcode"]["base64"]
        
        if "," in qr_b64:
            qr_b64 = qr_b64.split(",")[1]
            
        with open(nome_imagem, "wb") as f:
            f.write(base64.b64decode(qr_b64))
            
        print("✅ QR CODE PRONTO!")
        print("👉 ABRA A IMAGEM E ESCANEIE AGORA MESMO!")
    else:
        print(f"❌ Erro {res.status_code}: {res.text}")
        
except Exception as e:
    print(f"❌ Erro de conexão: {e}")