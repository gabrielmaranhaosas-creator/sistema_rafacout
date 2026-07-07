import streamlit as st
from groq import Groq
import os
import json

# ======================================================================
# 1. CAMADA DE CONFIGURAÇÃO (core/config.py)
# ======================================================================
st.set_page_config(page_title="Motor FSM - Produção", page_icon="⚙️", layout="centered")

class Config:
    @staticmethod
    def get_groq_key() -> str:
        chave = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
        if not chave:
            st.error("🚨 ERRO ARQUITETURAL: Chave GROQ_API_KEY ausente.")
            st.stop()
        return chave

# ======================================================================
# 2. CAMADA DE CONTEÚDO: ROTEIROS EXATOS (prompts/pablo_templates.py)
# ======================================================================
class RoteirosPablo:
    """Strings exatas do manual comercial. Nenhuma IA tem permissão de alterar isso."""
    
    SAUDACAO = "Boa tarde! Meu nome é Pablo e sou o empresário de Rafa, tudo bem!? Obrigado pelo contato e interesse. Em que posso ajudar? 😊"
    
    INDECISO = "Perfeito! Fico no aguardo das informações para podermos dar andamento. Qualquer dúvida, estou à disposição! 😊"
    
    COLETA_DADOS = "Para confirmar a disponibilidade e passar a proposta, eu preciso complementar algumas informações: {campos_faltantes}. Consegue me passar? 😃"
    
    GATILHO_PRE_PROPOSTA = (
        "Obrigado por todas as informações! Vou verificar a disponibilidade na nossa agenda para você. "
        "Enquanto monto a proposta para verificarmos, deixa te perguntar: você já conhece o show de Rafa? "
        "Rafa tem um repertório bem abrangente, podendo 'passear' por várias estilos (sertanejo, forró, axé, pagode, swingueira etc.). "
        "Nossa proposta é ser aquela banda que anima a pista ou mantém ela com a energia lá em cima. "
        "Posso mandar uma lista de repertório para vocês terem uma ideia e, caso fechem, podemos marcar uma reunião para falar especificamente sobre esse tema? 😊"
    )

# ======================================================================
# 3. CAMADA DE INFRAESTRUTURA NLU (services/nlu_engine.py)
# ======================================================================
class NLUEngine:
    """Extrai intenções e entidades via JSON Mode. Não gera diálogo."""
    
    EXTRACTION_PROMPT = """
    Você é um Motor de Compreensão de Linguagem Natural (NLU).
    Sua única função é ler a mensagem do usuário e extrair dados no formato JSON OBRIGATÓRIO.
    Não gere nenhum texto adicional.
    
    INTENCOES VALIDADAS:
    - "saudacao": Cliente apenas cumprimentou (oi, bom dia).
    - "indeciso": Cliente disse que não sabe, vai confirmar depois ou pediu tempo.
    - "informacao": Cliente enviou dados ou pediu orçamento.
    
    FORMATO OBRIGATÓRIO DE SAÍDA:
    {
        "intencao": "saudacao | indeciso | informacao",
        "entidades": {
            "tipo_evento": "valor extraído ou null",
            "data": "valor extraído ou null",
            "local": "valor extraído ou null",
            "horario": "valor extraído ou null"
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
                response_format={"type": "json_object"},
                max_tokens=200
            )
            raw_json = response.choices[0].message.content
            return json.loads(raw_json)
        except Exception as e:
            st.error(f"Falha de NLU: {e}")
            return {"intencao": "informacao", "entidades": {}}

# ======================================================================
# 4. MÁQUINA DE ESTADOS FINITA - O MOTOR DO PYTHON (core/fsm.py)
# ======================================================================
class PabloFSM:
    """Motor de regras em Python puro. Controla 100% do fluxo."""
    
    MAPA_CAMPOS = {
        "tipo_evento": "Nome do evento",
        "data": "Data exata",
        "local": "Local exato",
        "horario": "Horário previsto para o show"
    }

    def processar_estado(self, intencao: str, entidades_extraidas: dict, estado_memoria: dict) -> str:
        # 1. Atualiza memória nativa
        for chave, valor in entidades_extraidas.items():
            if valor is not None and str(valor).strip().lower() not in ["null", "none", "não informado", "nao informado"]:
                estado_memoria[chave] = valor
        
        # 2. Transição A: Indeciso
        if intencao == "indeciso":
            return RoteirosPablo.INDECISO

        # 3. Transição B: Saudação Inicial (Evita loop)
        if intencao == "saudacao":
            if not estado_memoria.get("ja_cumprimentou"):
                estado_memoria["ja_cumprimentou"] = True
                return RoteirosPablo.SAUDACAO
            # Se já cumprimentou e mandou oi de novo, assume que quer informação
            pass 

        # 4. Transição C: Avaliação de Dados Faltantes
        campos_pendentes = []
        for chave_tecnica, nome_comercial in self.MAPA_CAMPOS.items():
            if not estado_memoria.get(chave_tecnica):
                campos_pendentes.append(nome_comercial)

        if campos_pendentes:
            texto_faltante = ", ".join(campos_pendentes)
            return RoteirosPablo.COLETA_DADOS.format(campos_faltantes=texto_faltante)

        # 5. Transição D: Gatilho Final (Tudo Preenchido)
        return RoteirosPablo.GATILHO_PRE_PROPOSTA

# ======================================================================
# 5. CAMADA DE APRESENTAÇÃO (Interface Streamlit)
# ======================================================================
st.title("📱 Atendimento Oficial - Rafa Cout")
st.caption("Arquitetura FSM: IA atuando apenas como extrator de dados. Python controla o output.")
st.divider()

nlu = NLUEngine()
fsm = PabloFSM()

# Inicialização da Memória de Estado Limpa
if "memoria_lead" not in st.session_state:
    st.session_state.memoria_lead = {
        "ja_cumprimentou": False,
        "tipo_evento": None,
        "data": None,
        "local": None,
        "horario": None
    }
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Renderiza Interface
for msg in st.session_state.chat_history:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Loop de Eventos
if prompt := st.chat_input("Mensagem do cliente..."):
    # Renderiza User
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.spinner("Processando Inteligência NLU..."):
        # 1. NLU Extrai Intenção (Sem gerar texto final)
        analise_ia = nlu.analisar_mensagem(st.session_state.chat_history)
        
        # 2. Python (FSM) Decide a Resposta
        resposta_oficial = fsm.processar_estado(
            intencao=analise_ia.get("intencao", "informacao"),
            entidades_extraidas=analise_ia.get("entidades", {}),
            estado_memoria=st.session_state.memoria_lead
        )

        # DEBUG INVISÍVEL: Para você acompanhar o cérebro operando
        debug_info = f"\n\n\n`[STATUS DO MOTOR: Intenção: {analise_ia.get('intencao')} | Memória: {st.session_state.memoria_lead}]`"
        resposta_completa = resposta_oficial + debug_info

    # Renderiza Resposta Oficial
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(resposta_completa)
    
    st.session_state.chat_history.append({"role": "assistant", "content": resposta_completa})
