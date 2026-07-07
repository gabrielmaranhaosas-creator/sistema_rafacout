import requests

URL = "http://localhost:8080/instance/connectionState/MotorPablo"
HEADERS = {"apikey": "pablito123"}

def checar_motor():
    print("🔍 Verificando o status do Motor Pablo...\n")
    try:
        res = requests.get(URL, headers=HEADERS)
        if res.status_code == 200:
            dados = res.json()
            estado = dados.get("instance", {}).get("state", "Desconhecido")
            
            if estado == "open":
                print("✅ SUCESSO ABSOLUTO! O WhatsApp está CONECTADO!")
                print("🤖 O robô está pronto para receber mensagens.")
            elif estado == "connecting":
                print("⏳ O WhatsApp ainda está sincronizando... aguarde um momento.")
            else:
                print(f"⚠️ Status atual: {estado} (O celular pode ter desconectado)")
        else:
            print(f"❌ Erro na API: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Erro ao tentar conectar com a API: {e}")

if __name__ == "__main__":
    checar_motor()