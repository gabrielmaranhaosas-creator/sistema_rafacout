import streamlit as st
from groq import Groq
import os
import json

# ======================================================================
# 1. CAMADA DE CONFIGURAÇÃO E INTERFACE WEB
# ======================================================================
st.set_page_config(page_title="Motor FSM - Oficial Rafa Cout", page_icon="⚙️", layout="wide")

class Config:
    @staticmethod
    def get_groq_key() -> str:
        chave = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
        if not chave:
            st.error("🚨 ERRO ARQUITETURAL: Chave GROQ_API_KEY ausente.")
            st.stop()
        return chave

# ======================================================================
# 2. CAMADA DE NEGÓCIOS: ROTEIROS EXATOS DO DOCUMENTO
# ======================================================================
class RoteirosPablo:
    """Strings imutáveis retiradas literalmente do manual comercial de Rafa Cout."""
    
    # Situação 1: Apenas "Oi"
    SAUDACAO_SIMPLES = "Boa tarde {nome_cliente}. Meu nome é Pablo e sou o empresário de Rafa, tudo bem!? Obrigado pelo contato e interesse. Em que posso ajudar?"
    
    # Situação 2: Orçamento sem dados (Primeiro contato)
    ORCAMENTO_SEM_DADOS_NOVO = "Olá, {nome_cliente}. Aqui é o Pablo, empresário de Rafa Cout, tudo bem?! Obrigado pelo contato. Para confirmar a disponibilidade e passar a proposta, eu preciso de algumas informações: Nome do evento, Data, Local e Horário previsto para o show. Consegue me passar?"
    
    # Situação Parcial: Faltam informações (Primeiro contato)
    PARCIAL_NOVO = "Olá, {nome_cliente}. Aqui é o Pablo, empresário de Rafa Cout, tudo bem?! Obrigado pelo contato. Para confirmar a disponibilidade e passar a proposta, eu preciso complementar algumas informações: {campos_faltantes}. Consegue me passar?"
    
    # Situação Parcial: Faltam informações (Já se apresentou)
    PARCIAL_CONTINUACAO = "Para confirmar a disponibilidade e passar a proposta, eu preciso complementar algumas informações: {campos_faltantes}. Consegue me passar?"

    # Confirmações Específicas
    CONFIRMA_HORARIO = "Para confirmar a disponibilidade, o horário que você me informou é de início da festa ou de início do nosso show?"
    CONFIRMA_LOCAL = "Pode me confirmar o local exato do evento?"
    CONFIRMA_CORP_SEM_EMPRESA = "Pode me informar o nome da empresa e do evento para que eu possa colocar corretamente na proposta e em nossa agenda?"
    CONFIRMA_CORP_COM_EMPRESA = "Pode me informar o nome do evento para que eu possa colocar corretamente na proposta e em nossa agenda?"
    CONFIRMA_CASAMENTO = "Pode me informar o nome do casal para que eu possa colocar corretamente na proposta e em nossa agenda?"
    CONFIRMA_ANIVERSARIO = "Pode me informar o nome do/da aniversariante que eu possa colocar corretamente na proposta e em nossa agenda?"

    # Gatilho Final
    PRE_PROPOSTA = "Enquanto monto a proposta, deixa te perguntar: você já conhece o show de Rafa? Rafa tem um repertório bem abrangente, podendo \"passear\" por várias estilos (sertanejo, forró, axé, pagode, swingueira etc.). Nossa proposta é ser aquela banda que anima a pista ou mantém ela com a energia lá em cima. Posso mandar uma lista de repertório para vocês terem uma ideia e, caso fechem, podemos marcar uma reunião para falar especificamente sobre esse tema"

# ======================================================================
# 3. CAMADA DE INFRAESTRUTURA NLU (Extração JSON isolada)
# ======================================================================
class NLUEngine:
    """Motor de Compreensão. Extrai dados, NUNCA gera a resposta final."""
    
    EXTRACTION_PROMPT = """
    Você é um extrator de dados JSON. Leia o histórico da conversa e a última mensagem do usuário.
    Extraia as informações e atualize o estado. NÃO gere texto. Responda APENAS em JSON válido.

    REGRAS DE EXTRAÇÃO:
    - "intencao": Use "oi_simples" se ele apenas cumprimentou sem pedir nada. Use "orcamento" se ele quer valores/disponibilidade. Use "informacao" se ele está apenas respondendo dados.
    - "nome_cliente": O nome do cliente, se informado.
    - "tipo_evento": (ex: Casamento, Corporativo, Aniversário, 15 Anos, Formatura).
    - "data": Data exata (dia, mês e ano). Se faltar o ano, deixe como null.
    - "local": Cidade e Nome da Casa de Festas. Se faltar a casa de festas, deixe como null.
    - "horario_show": Horário de início DO SHOW (se ele informou o horário da festa, deixe null).
    - "nome_homenageado": Nome do casal, empresa ou aniversariante.

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
        except Exception as e:
            st.error(f"Falha de NLU (JSON Parsing): {e}")
            return {"intencao": "informacao", "entidades": {}}

# ======================================================================
# 4. MÁQUINA DE ESTADOS FINITA (O Cérebro em Python)
# ======================================================================
class PabloFSM:
    """Motor Python que determina a string exata a ser impressa."""
    
    def processar_estado(self, intencao: str, entidades: dict, memoria: dict) -> str:
        # 1. Atualiza a memória com o que a NLU encontrou
        for k, v in entidades.items():
            if v and str(v).lower() not in ["null", "none"]:
                memoria[k] = v

        nome = memoria.get("nome_cliente", "").strip()
        tratamento_nome = f" {nome}" if nome else ""

        # 2. Avaliação de Intenção Inicial
        if intencao == "oi_simples" and not memoria["ja_se_apresentou"]:
            memoria["ja_se_apresentou"] = True
            return RoteirosPablo.SAUDACAO_SIMPLES.format(nome_cliente=tratamento_nome).replace(" .", ".").replace("  ", " ")

        # 3. Avaliação dos 4 Pilares Fundamentais
        campos_faltantes = []
        if not memoria.get("tipo_evento"): campos_faltantes.append("Nome do evento")
        if not memoria.get("data"): campos_faltantes.append("Data completa (com ano)")
        if not memoria.get("local"): campos_faltantes.append("Local (Cidade e Casa de Festas)")
        if not memoria.get("horario_show"): campos_faltantes.append("Horário previsto para o show")

        # 4. Se faltam dados cruciais
        if campos_faltantes:
            texto_faltantes = ", ".join(campos_faltantes)
            if len(campos_faltantes) == 4 and not memoria["ja_se_apresentou"]:
                memoria["ja_se_apresentou"] = True
                return RoteirosPablo.ORCAMENTO_SEM_DADOS_NOVO.format(nome_cliente=tratamento_nome).replace(" .", ".").replace("  ", " ")
            elif not memoria["ja_se_apresentou"]:
                memoria["ja_se_apresentou"] = True
                return RoteirosPablo.PARCIAL_NOVO.format(nome_cliente=tratamento_nome, campos_faltantes=texto_faltantes).replace(" .", ".").replace("  ", " ")
            else:
                return RoteirosPablo.PARCIAL_CONTINUACAO.format(campos_faltantes=texto_faltantes)

        # 5. Micro-validações (Se os 4 pilares estão preenchidos, validamos os detalhes)
        tipo = str(memoria.get("tipo_evento", "")).lower()
        if not memoria.get("nome_homenageado"):
            if "casamento" in tipo:
                return RoteirosPablo.CONFIRMA_CASAMENTO
            elif "anivers" in tipo or "15 anos" in tipo:
                return RoteirosPablo.CONFIRMA_ANIVERSARIO
            elif "corporativo" in tipo:
                return RoteirosPablo.CONFIRMA_CORP_SEM_EMPRESA

        # 6. Tudo validado: Gatilho Final
        return RoteirosPablo.PRE_PROPOSTA

# ======================================================================
# 5. RENDERIZAÇÃO DA INTERFACE (Separação UI / Core)
# ======================================================================
col_chat, col_debug = st.columns([2, 1])

with col_chat:
    st.title("📱 Atendimento Oficial - Rafa Cout")
    st.caption("Arquitetura FSM Estrita: O texto gerado vem 100% do código Python.")

    nlu = NLUEngine()
    fsm = PabloFSM()

    if "memoria_lead" not in st.session_state:
        st.session_state.memoria_lead = {
            "ja_se_apresentou": False,
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

        with st.spinner("Processando NLU..."):
            # O LLM extrai o JSON silenciosamente
            analise_json = nlu.analisar_mensagem(st.session_state.chat_history)
            
            # O Python seleciona a string exata
            resposta_oficial = fsm.processar_estado(
                intencao=analise_json.get("intencao", "informacao"),
                entidades=analise_json.get("entidades", {}),
                memoria=st.session_state.memoria_lead
            )

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(resposta_oficial)
        
        st.session_state.chat_history.append({"role": "assistant", "content": resposta_oficial})

# A telemetria foi movida para uma coluna lateral isolada
with col_debug:
    st.markdown("### 🔍 Telemetria Invisível")
    st.caption("Este painel simula o banco de dados. O lead não vê isso no WhatsApp.")
    st.json(st.session_state.memoria_lead)
