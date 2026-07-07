import streamlit as st
from groq import Groq
import os

# ==========================================
# 1. CONFIGURAÇÃO DA INTERFACE WEB
# ==========================================
st.set_page_config(
    page_title="Motor Pablo - Atendimento Oficial", 
    page_icon="📱", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("📱 Atendimento Oficial - Rafa Cout")
st.caption("Motor V8: Com injeção dinâmica de contexto via Python para bloqueio de loops.")
st.divider()

# ==========================================
# 2. INICIALIZAÇÃO DO MOTOR
# ==========================================
@st.cache_resource
def iniciar_cliente_groq():
    chave = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
    if not chave:
        st.error("🚨 Falha de Autenticação: A chave GROQ_API_KEY não foi encontrada nos Secrets.")
        st.stop()
    return Groq(api_key=chave)

client = iniciar_cliente_groq()

# ==========================================
# 3. CORE COGNITIVO (BASE DINÂMICA)
# ==========================================
# Retiramos as condicionais falhas. A lógica será injetada em tempo de execução.
BASE_PROMPT = """
Você é Pablo Bezerra, empresário do cantor Rafa Cout. Seu objetivo é triagem comercial via WhatsApp.

# 1. OS 4 PILARES DA TRIAGEM (NUNCA AVANCE SEM ELES)
1. NOME/TIPO DO EVENTO: (Casamento, Corporativo, Aniversário, etc.)
2. DATA: Dia, mês e ano.
3. LOCAL: Cidade e nome da casa de festas.
4. HORÁRIO: Início do show.

# 2. ROTEIROS DE RESPOSTA (USE AS PALAVRAS EXATAS DO ROTEIRO, NÃO INVENTE)

SITUAÇÃO A - Cliente disse APENAS "Oi": 
"Boa tarde! Meu nome é Pablo e sou o empresário de Rafa, tudo bem!? Obrigado pelo contato e interesse. Em que posso ajudar? 😊"

SITUAÇÃO B - Faltam dados na solicitação de orçamento:
"Para confirmar a disponibilidade e passar a proposta, eu preciso complementar algumas informações: [INSERIR APENAS O QUE FALTA AQUI]. Consegue me passar? 😃"

SITUAÇÃO C - Cliente enviou tudo, mas exige micro-validação (faça uma por vez):
- Horário: "Para confirmar a disponibilidade, o horário que você me informou é de início da festa ou de início do nosso show? 😊"
- Local: "Pode me confirmar o local exato (nome da casa de festas) do evento? 😃"
- Corporativo (sem empresa): "Pode me informar o nome da empresa e do evento para que eu possa colocar na proposta?"
- Casamento: "Pode me informar o nome do casal?"
- Aniversário: "Pode me informar o nome da(o) aniversariante?"

SITUAÇÃO D - Cliente não sabe / vai pensar:
"Perfeito! Fico no aguardo das informações para podermos dar andamento. Qualquer dúvida, estou à disposição! 😊"

SITUAÇÃO E - Gatilho Final (Tudo validado):
"Enquanto monto a proposta, deixa te perguntar: você já conhece o show de Rafa? Rafa tem um repertório bem abrangente, podendo 'passear' por várias estilos (sertanejo, forró, axé, pagode, swingueira etc.). Nossa proposta é ser aquela banda que anima a pista ou mantém ela com a energia lá em cima. Posso mandar uma lista de repertório para vocês terem uma ideia e, caso fechem, podemos marcar uma reunião para falar especificamente sobre esse tema? 😊"

# 3. REGRAS ABSOLUTAS
- NUNCA emende duas situações em uma única mensagem.
- {INJECAO_DINAMICA_DE_SAUDACAO}

# 4. TAGS OBRIGATÓRIAS (Pule 2 linhas no final e imprima)
[TIPO_EVENTO: valor]
[DATA: valor]
[LOCAL: valor]
[HORARIO: valor]
"""

# ==========================================
# 4. GERENCIAMENTO DE MEMÓRIA DE SESSÃO
# ==========================================
# Separamos o chat_history das mensagens da API para podermos manipular o System Prompt
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Renderiza o chat na interface
for msg in st.session_state.chat_history:
    avatar_icon = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])

# ==========================================
# 5. EXECUÇÃO DO MOTOR COM INJEÇÃO DINÂMICA
# ==========================================
if prompt := st.chat_input("Mensagem do cliente (Ex: Oi, Quero um orçamento, etc...)"):
    
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # ---------------------------------------------------------
    # A MÁGICA ARQUITETURAL ACONTECE AQUI
    # ---------------------------------------------------------
    # O Python verifica fisicamente se a palavra "Pablo" já existe nas respostas do bot
    ja_se_apresentou = any("Pablo" in msg["content"] for msg in st.session_state.chat_history if msg["role"] == "assistant")
    
    if ja_se_apresentou:
        # Se já se apresentou, bloqueamos o LLM de gerar qualquer saudação novamente
        trava = "REGRA CRÍTICA: Você JÁ se apresentou. É EXPRESSAMENTE PROIBIDO escrever 'Aqui é o Pablo', 'Meu nome é Pablo' ou 'Obrigado pelo contato'. Comece a frase DIRETAMENTE respondendo o cliente ou pedindo os dados."
    else:
        # Se é a primeira mensagem e ele pediu orçamento direto, forçamos a saudação
        trava = "REGRA CRÍTICA: É o seu primeiro contato. Se o cliente já pediu orçamento, INICIE a frase com 'Olá! Aqui é o Pablo, empresário de Rafa Cout, tudo bem?! Obrigado pelo contato.' ANTES de ir para a SITUAÇÃO B."

    # Substitui a tag no prompt base pela regra calculada agora
    system_prompt_calculado = BASE_PROMPT.replace("{INJECAO_DINAMICA_DE_SAUDACAO}", trava)
    
    # Monta a lista final para a API (Prompt recém calculado + Histórico do usuário)
    api_messages = [{"role": "system", "content": system_prompt_calculado}] + st.session_state.chat_history
    
    try:
        with st.spinner("Processando lógica..."):
            chat_completion = client.chat.completions.create(
                messages=api_messages,
                model="llama-3.3-70b-versatile",
                temperature=0.0,
                max_tokens=600,
                presence_penalty=0.0,
                frequency_penalty=0.0
            )
            
        resposta_ia = chat_completion.choices[0].message.content
        
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(resposta_ia)
            
        st.session_state.chat_history.append({"role": "assistant", "content": resposta_ia})
        
    except Exception as e:
        st.error(f"Falha Crítica no Motor de Inferência: {str(e)}")
