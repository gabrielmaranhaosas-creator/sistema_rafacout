from fastapi import FastAPI, HTTPException
from models.schemas import WhatsAppMessage
from agents.atendimento import agente_atendimento
from utils.pdf_generator import gerar_pdf_proposta
import database
import asyncio
import random
import re
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Pablito V8 - Sistema de Alta Performance Rafa Cout")

@app.on_event("startup")
async def startup_event():
    logger.info("Motor V8 Iniciado. Inicializando infraestrutura de Banco de Dados...")
    await database.inicializar_db()

async def simular_humanizacao(mensagem_cliente: str, resposta_limpa: str):
    """Motor Heurístico de Humanização de Latência"""
    palavras_cliente = len(mensagem_cliente.split())
    palavras_ia = len(resposta_limpa.split())
    
    tempo_leitura = palavras_cliente / 4.0 
    tempo_digitacao = palavras_ia / 2.5
    tempo_calculado = tempo_leitura + tempo_digitacao + random.uniform(1.0, 3.0)
    
    atraso_real = min(tempo_calculado, 10.0) # Teto expandido sutilmente para respostas que exigem mais digitação
    logger.info(f"Stealth Mode ativado: Simulando digitação por {atraso_real:.1f}s...")
    await asyncio.sleep(atraso_real)

@app.post("/webhook/whatsapp")
async def processar_mensagem(payload: WhatsAppMessage):
    try:
        logger.info(f"Webhook (V8) recebido de: {payload.name} ({payload.wa_id})")

        # 1. Hidratação Assíncrona do Lead
        lead_data_bd = await database.obter_ou_criar_lead(payload.wa_id, payload.name)
        lead = {
            "event_type": lead_data_bd[2], 
            "event_date": lead_data_bd[3],
            "location": lead_data_bd[4], 
            "event_time": lead_data_bd[5]
        }

        # 2. Processamento Cognitivo Assíncrono
        resposta_bruta = await agente_atendimento.gerar_resposta(
            wa_id=payload.wa_id, 
            nome_cliente=payload.name, 
            mensagem_cliente=payload.text, 
            lead_data=lead
        )

        # 3. Sincronização de Estado (Regex Seguro)
        tags_map = {
            "TIPO_EVENTO": "event_type", "DATA": "event_date", 
            "LOCAL": "location", "HORARIO": "event_time"
        }
        for tag, coluna in tags_map.items():
            match = re.search(fr"\[{tag}:\s*(.*?)\]", resposta_bruta, re.IGNORECASE)
            if match:
                valor_extraido = match.group(1).strip()
                if valor_extraido and valor_extraido.lower() != "não informado":
                    await database.atualizar_lead(payload.wa_id, coluna, valor_extraido)

        # 4. Limpeza da string para o cliente
        resposta_limpa = re.sub(r"\[.*?\]", "", resposta_bruta).strip()

        # 5. Simulador Anti-Bot
        await simular_humanizacao(payload.text, resposta_limpa)

        # 6. Interceptador de Estado Terminal (AUTORIDADE COGNITIVA ABSOLUTA)
        if "gerando a sua proposta oficial" in resposta_limpa.lower():
            logger.info(f"Gatilho de Proposta Comercial ATIVADO para {payload.wa_id}")
            
            lead_atualizado = await database.obter_ou_criar_lead(payload.wa_id, payload.name)
            
            try:
                pdf_path = gerar_pdf_proposta({
                    "wa_id": lead_atualizado[0], 
                    "name": lead_atualizado[1], 
                    "event_type": lead_atualizado[2] or "Evento", 
                    "event_date": lead_atualizado[3] or "A definir", 
                    "location": lead_atualizado[4] or "A definir", 
                    "event_time": lead_atualizado[5] or "A definir"
                })
            except Exception as pdf_error:
                logger.error(f"Erro no módulo de PDF, gerando proposta de contorno: {pdf_error}")
                pdf_path = "proposta_padrao.pdf"
            
            await database.definir_proposta_enviada(payload.wa_id)
            
            msg_ancoragem = (
                "Excelente!\n\n"
                "📄 Segue a proposta detalhada anexa. O nosso cachê padrão para essa data e local é R$ 15.000,00, "
                "mas para fecharmos agora, consegui uma condição especial de R$ 13.000,00 para você! 😊"
            )
            return {"status": "proposta_gerada", "response": msg_ancoragem, "pdf_link": pdf_path}

        return {"status": "seguindo_atendimento", "response": resposta_limpa}

    except Exception as e:
        logger.error(f"Falha Crítica no Orquestrador: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno de processamento.")