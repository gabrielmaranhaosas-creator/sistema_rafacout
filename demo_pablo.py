import streamlit as st
from groq import Groq
import os
import json
from datetime import datetime, timedelta

# ======================================================================
# 1. CAMADA DE CONFIGURAÇÃO E INTERFACE WEB
# ======================================================================
st.set_page_config(page_title="Motor FSM - Oficial Rafa Cout", page_icon="⚙️", layout="wide")

class Config:
    @staticmethod
    def get_groq_key() -> str:
        chave = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
        if not chave:
            st.error("🚨 ERRO ARQUITETURAL: Chave GROQ_API_KEY ausente nos Secrets.")
            st.stop()
        return chave

# ======================================================================
# 2. CAMADA DE NEGÓCIOS: ROTEIROS EXATOS DO DOCUMENTO
# ======================================================================
class RoteirosPablo:
    """Strings imutáveis, agora com Estado de Pós-Proposta (Human Handoff)."""
    
    SAUDACAO_SIMPLES = "{saudacao_tempo}{nome_cliente}! Meu nome é Pablo e sou o empresário de Rafa, tudo bem!? Obrigado pelo contato e interesse. Em que posso ajudar?"
    ORCAMENTO_SEM_DADOS_NOVO = "{saudacao_tempo}{nome_cliente}! Aqui é o Pablo, empresário de Rafa Cout, tudo bem?! Obrigado pelo contato. Para confirmar a disponibilidade e passar a proposta, eu preciso de algumas informações: Nome do evento, Data, Local e Horário previsto para o show. Consegue me passar?"
    PARCIAL_NOVO = "{saudacao_tempo}{nome_cliente}! Aqui é o Pablo, empresário de Rafa Cout, tudo bem?! Obrigado pelo contato. Para confirmar a disponibilidade e passar a proposta, eu preciso complementar algumas informações: {campos_faltantes}. Consegue me passar?"
    PARCIAL_CONTINUACAO = "Para confirmar a disponibilidade e passar a proposta, eu preciso complementar algumas informações: {campos_faltantes}. Consegue me passar?"
    CONFIRMA_HORARIO = "Para confirmar a disponibilidade, o horário que você me informou é de início da festa ou de início do nosso show?"
    CONFIRMA_LOCAL = "Pode me confirmar o local exato do evento?"
    CONFIRMA_CORP_SEM_EMPRESA = "Pode me informar o nome da empresa e do evento para que eu possa colocar corretamente na proposta e em nossa agenda?"
    CONFIRMA_CASAMENTO = "Pode me informar o nome do casal para que eu possa colocar corretamente na proposta e em nossa agenda?"
    CONFIRMA_ANIVERSARIO = "Pode me informar o nome do/da aniversariante que eu possa colocar corretamente na proposta e em nossa agenda?"
    
    PRE_PROPOSTA = "Enquanto monto a proposta, deixa te perguntar: você já conhece o show de Rafa? Rafa tem um repertório bem abrangente, podendo \"passear\" por várias estilos (sertanejo, forró, axé, pagode, swingueira etc.). Nossa proposta é ser aquela banda que anima a pista ou mantém ela com a energia lá em cima. Posso mandar uma lista de repertório para vocês terem uma ideia e, caso fechem, podemos marcar uma reunião para falar especificamente sobre esse tema"
    
    PONTE_CONVERSACIONAL = "Perfeito! Vou separar alguns materiais nossos para te enviar, assim vocês conseguem sentir um pouco mais da nossa energia. 🎶\n\nE conforme conversamos, "
    
    # Adicionado o Mock de Anexo de PDF
    PROPOSTA_PADRAO = "{saudacao_proposta}segue a proposta para a realização do show de Rafa no {evento}, no dia *{data_horario}, no {local}.*\n\n*[📎 ARQUIVO PDF ANEXADO: Proposta_Rafa_Cout.pdf]*\n\nMais uma vez agradecemos o interesse e espero podermos levar a energia de Rafa para esse dia tão especial.😃\n\nQualquer dúvida ou ajuda, estou à disposição. Fico no seu aguardo.😊"
    
    # Novo Roteiro: Graceful Degradation pós-envio
    POS_PROPOSTA_FALLBACK = "Opa! O arquivo em PDF com todos os valores e detalhes da estrutura foi enviado logo acima. 👆 Consegue visualizar por aí? Qualquer dúvida sobre a proposta, é só me falar! 😊"

# ======================================================================
# 3. CAMADA DE INFRAESTRUTURA NLU (Extração JSON isolada)
# ======================================================================
class NLUEngine:
    EXTRACTION_PROMPT = """
    Você é um extrator de dados JSON. Leia o histórico da conversa.
    Extraia as informações e atualize o estado. NÃO gere texto. Responda APENAS em JSON válido.

    REGRAS CRÍTICAS DE EXTRAÇÃO:
    - "data": Mantenha EXATAMENTE o formato natural (ex: "18 de dezembro de 2026"). NÃO use padrão ISO.
    - "horario_show": Mantenha EXATAMENTE o formato natural (ex: "22 horas", "1 da manhã").
    - "nome_cliente": O nome da pessoa perguntando. REGRA ABSOLUTA: O SEU NOME É PABLO E O ARTISTA É RAFA. NUNCA atribua "Pablo" ou "Rafa" como nome do cliente. Se não souber, preencha com null.
    - "intencao": Use "oi_simples" se cumprimentou sem pedir nada. Use "orcamento" se quer valores. Use "informacao" se deu dados.

    FORMATO DE SAÍDA OBRIGATÓRIO:
    {
        "intencao": "oi_simples | orcamento | informacao",
        "entidades": {
            "nome_cliente": "valor ou null",
            "tipo_evento": "valor ou null",
            "data": "valor ou null",
            "local": "valor ou null",
            "horario_show": "valor ou null",
            "nome_homenageado": "valor ou null"
        }
    }
    """
    def __init__(self):
        self.client = Groq(api_key=Config.get_groq_key())

    def analisar_mensagem(self, historico: list) -> dict:
        messages = [{"role": "system", "content": self.EXTRACTION_PROMPT}] + historico
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {"intencao": "informacao", "entidades": {}}

# ======================================================================
# 4. MÁQUINA DE ESTADOS FINITA (O Cérebro em Python)
# ======================================================================
class PabloFSM:
    def processar_estado(self, intencao: str, entidades: dict, memoria: dict) -> str:
        for k, v in entidades.items():
            if v and str(v).lower() not in ["null", "none"]:
                memoria[k] = v

        nome_raw = memoria.get("nome_cliente")
        if nome_raw and str(nome_raw).strip().lower() in ["pablo", "rafa", "rafa cout"]:
            nome_raw = None
            memoria["nome_cliente"] = None
            
        if not nome_raw and memoria.get("nome_homenageado"):
            if str(memoria.get("nome_homenageado")).strip().lower() not in ["pablo", "rafa", "rafa cout"]:
                nome_raw = memoria.get("nome_homenageado")

        hora_atual = (datetime.utcnow() - timedelta(hours=3)).hour
        if hora_atual < 12: saudacao_tempo = "Bom dia"
        elif hora_atual < 18: saudacao_tempo = "Boa tarde"
        else: saudacao_tempo = "Boa noite"

        nome = str(nome_raw).strip().title() if nome_raw and str(nome_raw).lower() not in ["null", "none"] else ""
        tratamento_nome = f", {nome}" if nome else ""
        saudacao_proposta = f"{nome}, " if nome else ""

        # TRANSIÇÃO 1: ESTADO PÓS-PROPOSTA (Human Handoff Graceful Degradation)
        if memoria.get("proposta_enviada"):
            return RoteirosPablo.POS_PROPOSTA_FALLBACK

        # TRANSIÇÃO 2: ENVIO DA PROPOSTA
        if memoria.get("pre_proposta_enviada"):
            memoria["proposta_enviada"] = True
            
            evento_raw = memoria.get("tipo_evento", "evento")
            evento = str(evento_raw).strip().title() if evento_raw else "evento"
            data = str(memoria.get("data", "")).strip()
            horario = str(memoria.get("horario_show", "")).strip()
            local = str(memoria.get("local", "")).strip().title()
            
            proposta_texto = RoteirosPablo.PROPOSTA_PADRAO.format(
                saudacao_proposta=saudacao_proposta,
                evento=evento,
                data_horario=f"{data} às {horario}",
                local=local
            )
            return RoteirosPablo.PONTE_CONVERSACIONAL + proposta_texto

        # TRANSIÇÃO 3: SAUDAÇÃO
        if intencao == "oi_simples" and not memoria.get("ja_se_apresentou"):
            memoria["ja_se_apresentou"] = True
            return RoteirosPablo.SAUDACAO_SIMPLES.format(saudacao_tempo=saudacao_tempo, nome_cliente=tratamento_nome).replace(" .", ".")

        # TRANSIÇÃO 4: AVALIAÇÃO DE DADOS FALTANTES
        campos_faltantes = []
        if not memoria.get("tipo_evento"): campos_faltantes.append("Nome do evento")
        if not memoria.get("data"): campos_faltantes.append("Data completa (com ano)")
        if not memoria.get("local"): campos_faltantes.append("Local (Cidade e Casa de Festas)")
        if not memoria.get("horario_show"): campos_faltantes.append("Horário previsto para o show")

        if campos_faltantes:
            texto_faltantes = ", ".join(campos_faltantes)
            if len(campos_faltantes) == 4 and not memoria.get("ja_se_apresentou"):
                memoria["ja_se_apresentou"] = True
                return RoteirosPablo.ORCAMENTO_SEM_DADOS_NOVO.format(saudacao_tempo=saudacao_tempo, nome_cliente=tratamento_nome).replace(" .", ".")
            elif not memoria.get("ja_se_apresentou"):
                memoria["ja_se_apresentou"] = True
                return RoteirosPablo.PARCIAL_NOVO.format(saudacao_tempo=saudacao_tempo, nome_cliente=tratamento_nome, campos_faltantes=texto_faltantes).replace(" .", ".")
            else:
                return RoteirosPablo.PARCIAL_CONTINUACAO.format(campos_faltantes=texto_faltantes)

        # TRANSIÇÃO 5: MICRO-VALIDAÇÕES
        tipo = str(memoria.get("tipo_evento") or "").lower()
        if not memoria.get("nome_homenageado"):
            if "casamento" in tipo: return RoteirosPablo.CONFIRMA_CASAMENTO
            elif "anivers" in tipo or "15 anos" in tipo: return RoteirosPablo.CONFIRMA_ANIVERSARIO
            elif "corporativo" in tipo: return RoteirosPablo.CONFIRMA_CORP_SEM_EMPRESA

        # TRANSIÇÃO 6: GATILHO DA PRÉ-PROPOSTA
        memoria["pre_proposta_enviada"] = True
        return RoteirosPablo.PRE_PROPOSTA

# ======================================================================
# 5. RENDERIZAÇÃO DA INTERFACE
# ======================================================================
col_chat, col_debug = st.columns([2, 1])

with col_chat:
    st.title("📱 Atendimento Oficial - Rafa Cout [BUILD V7 - FSM]")
    st.caption("FSM c/ Mock de Payload PDF e Fallback Pós-Proposta Humanizado.")

    nlu = NLUEngine()
    fsm = PabloFSM()

    if "memoria_lead" not in st.session_state:
        st.session_state.memoria_lead = {
            "ja_se_apresentou": False,
            "pre_proposta_enviada": False,
            "proposta_enviada": False,
            "nome_cliente": None, 
            "tipo_evento": None,
            "data": None, 
            "local": None, 
            "horario_show": None, 
            "nome_homenageado": None
        }
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Mensagem do cliente..."):
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.spinner("Processando NLU e Máquina de Estados..."):
            analise_json = nlu.analisar_mensagem(st.session_state.chat_history)
            resposta_oficial = fsm.processar_estado(
                intencao=analise_json.get("intencao", "informacao"),
                entidades=analise_json.get("entidades", {}),
                memoria=st.session_state.memoria_lead
            )

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(resposta_oficial)
        st.session_state.chat_history.append({"role": "assistant", "content": resposta_oficial})

with col_debug:
    st.markdown("### 🔍 Telemetria FSM")
    st.json(st.session_state.memoria_lead)