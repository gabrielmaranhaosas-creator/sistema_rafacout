import requests

# Configurações do seu servidor Evolution API
EVOLUTION_API_URL = "http://localhost:8080" 
INSTANCE_NAME = "pablito"
API_KEY = "sua_api_key_global_aqui"

def enviar_mensagem_texto(numero, texto):
    """Simula digitação e envia a resposta de texto."""
    url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    payload = {
        "number": numero,
        "options": {"delay": 1500, "presence": "composing"},
        "textMessage": {"text": texto}
    }
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Erro ao enviar mensagem para {numero}: {e}")

def enviar_pdf(numero, caminho_pdf, mensagem_caption):
    """Converte o PDF gerado em Base64 e despacha como documento no WhatsApp."""
    url = f"{EVOLUTION_API_URL}/message/sendMedia/{INSTANCE_NAME}"
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    
    import base64
    with open(caminho_pdf, "rb") as file:
        media_base64 = base64.b64encode(file.read()).decode('utf-8')
        
    payload = {
        "number": numero,
        "options": {"delay": 2000, "presence": "composing"},
        "mediaMessage": {
            "mediatype": "document",
            "fileName": "Proposta_Rafa_Cout.pdf",
            "caption": mensagem_caption,
            "media": media_base64
        }
    }
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Erro ao enviar PDF para {numero}: {e}")