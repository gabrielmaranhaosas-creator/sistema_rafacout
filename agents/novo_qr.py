import requests
import base64
import os
import time

URL_BASE = "http://localhost:8080"
INSTANCIA = "MotorPablo"
API_KEY = "pablito123"
HEADERS = {"apikey": API_KEY}

def gerar_novo_qr():
    print("🔄 A preparar uma ligação limpa...")
    
    # Força o logout de qualquer sessão travada
    try:
        requests.delete(f"{URL_BASE}/instance/logout/{INSTANCIA}", headers=HEADERS)
        time.sleep(2)
    except:
        pass

    print("⏳ A solicitar novo QR Code...")
    url_connect = f"{URL_BASE}/instance/connect/{INSTANCIA}"
    
    try:
        res = requests.get(url_connect, headers=HEADERS)
        if res.status_code in [200, 201]:
            data = res.json()
            if "base64" in data:
                qr_b64 = data["base64"]
                if "," in qr_b64:
                    qr_b64 = qr_b64.split(",")[1]
                
                with open("novo_qrcode.png", "wb") as f:
                    f.write(base64.b64decode(qr_b64))
                
                print("\n✅ QR CODE GERADO COM SUCESSO!")
                print("👉 Vá à pasta 'agents', abra a imagem 'novo_qrcode.png' e faça o scan com o telemóvel AGORA.")
            else:
                print("\n⚠️ Atenção: A API diz que o telemóvel já está conectado.")
                print(f"Detalhes: {data}")
        else:
            print(f"\n❌ Erro na API: {res.text}")
    except Exception as e:
        print(f"\n❌ Erro de ligação: {e}")

if __name__ == "__main__":
    # Limpa a imagem antiga se existir
    if os.path.exists("novo_qrcode.png"):
        os.remove("novo_qrcode.png")
    gerar_novo_qr()