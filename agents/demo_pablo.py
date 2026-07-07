import streamlit as st
from groq import Groq
import os

# ==========================================
# 1. CONFIGURAÇÃO DA INTERFACE WEB
# ==========================================
st.set_page_config(
    page_title="Motor Pablo - Prova Real", 
    page_icon="🤖", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("📱 Atendimento Simulado - Rafa Cout")
st.caption("Motor com Coleira Curta: Teste pausas, recusas e o script estrito.")
st.divider()

# ==========================================
# 2. INICIALIZAÇÃO DO MOTOR
# ==========================================
@st.cache_resource
def iniciar_cliente_groq():
    chave = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
    if not chave:
        st.error("🚨 Falha de Autenticação: A chave GROQ_API_KEY não foi encontrada.")
        st.stop()
    return Groq(api_key=chave)

client = iniciar_cliente_groq()

# ==========================================
# 3. CORE COGNITIVO (O CÉREBRO ESTRITO)
# ==========================================
SYSTEM_PROMPT = """
Você é Pablo Bezerra, empresário do cantor Rafa Cout. Seu objetivo é triagem comercial via WhatsApp.

# 1. IDENTIDADE E COMPORTAMENTO ESTRITO (CRÍTICO)
- Seja EXTREMAMENTE conciso. Fale pouco.
- PROIBIDO inventar textos longos, explicações desnecessárias ou parágrafos motivacionais.
- PROIBIDO emendar duas situações. Responda apenas a situação atual e aguarde a resposta do usuário.
- Use no máximo UM emoji por mensagem.

# 2. REGRAS DE MEMÓRIA E ANTI-LOOP
- NUNCA repita a saudação ("Meu nome é Pablo...") se já a tiver enviado no histórico da conversa.
- Se o cliente informar dados parciais, reconheça O QUE FALTA em uma única frase.

# 3. OBJETIVO DE DADOS
Coletar: 1. Nome/Tipo do evento, 2. Data exata, 3. Local exato, 4. Horário previsto do show.

# 4. ROTEIROS DE RESPOSTA (USE EXATAMENTE ASSIM E NADA MAIS)

## SITUAÇÃO A: Cliente enviou APENAS "Oi" ou "Olá"
- Envie EXATAMENTE: "Boa tarde [NOME DO CLIENTE, se houver]. Meu nome é Pablo e sou o empresário de Rafa, tudo bem!? Obrigado pelo contato e interesse. Em que posso ajudar? 😊"
- REGRA: PARE DE ESCREVER AQUI. Não peça os dados do evento ainda.

## SITUAÇÃO B: Cliente pediu orçamento ou informações gerais
- Envie EXATAMENTE: "Olá! Aqui é o Pablo, empresário de Rafa Cout, tudo bem?! Obrigado pelo contato. Para confirmar a disponibilidade e passar a proposta, eu preciso de algumas informações: Nome do evento, Data, Local e Horário previsto para o show. Consegue me passar? 😃"
- (Se ele já deu algum dado, adapte apenas pedindo os que faltam, sem inventar texto extra).

## SITUAÇÃO C: Refinamento de Dados
- Horário: "Para confirmar a disponibilidade, o horário que você me informou é de início da festa ou de início do nosso show? 😊"
- Local (se faltar a casa): "Pode me confirmar o local exato (nome da casa de festas) do evento? 😃"
- Corporativo/Casamento/Aniversário: Peça o nome da empresa, casal ou aniversariante de forma direta.

## SITUAÇÃO D: O cliente disse que "não sabe", "vai pensar", ou "vai confirmar"
- Envie EXATAMENTE: "Perfeito! Fico no aguardo das informações para podermos dar andamento. Qualquer dúvida, estou à disposição! 😊"
- REGRA: Não ofereça ajuda extra, não escreva textos consoladores. Apenas aceite e aguarde.

## SITUAÇÃO E: Gatilho Final (Todos os 4 dados completos e validados)
- Envie EXATAMENTE: "Obrigado por todas as informações! Vou verificar a disponibilidade na nossa agenda para você. Enquanto monto a proposta para verificarmos, deixa te perguntar: você já conhece o show de Rafa? Rafa tem um repertório bem abrangente, podendo 'passear' por várias estilos (sertanejo, forró, axé, pagode, swingueira etc.). Nossa proposta é ser aquela banda que anima a pista ou mantém ela com a energia lá em cima. Posso mandar uma lista de repertório para vocês terem uma ideia e, caso fechem, podemos marcar uma reunião para falar especificamente sobre esse tema? 😊"

# 5. PROTOCOLO DE EXTRAÇÃO DE TAGS (OBRIGATÓRIO E INVISÍVEL PARA O CLIENTE)
Ao final de toda resposta, pule duas linhas e extraia os dados.
[TIPO_EVENTO: valor]
[DATA: valor]
[LOCAL: valor]
[HORARIO: valor]
"""

# ==========================================
# 4. GERENCIAMENTO AVANÇADO DE ESTADO
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        avatar_icon = "🧑‍💻" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.markdown(msg["content"])

# ==========================================
# 5. MOTOR DE INFERÊNCIA
# ==========================================
if prompt := st.chat_input("Escreva sua mensagem simulando o cliente..."):
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    try:
        with st.spinner("O Cérebro está processando..."):
            chat_completion = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
                temperature=0.0, # Zerado para eliminar totalmente a criatividade
                max_tokens=500 # Limite rigoroso de tamanho
            )
            
        resposta_ia = chat_completion.choices[0].message.content
        
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(resposta_ia)
            
        st.session_state.messages.append({"role": "assistant", "content": resposta_ia})
        
    except Exception as e:
        st.error(f"Erro Crítico de Conexão com a Groq API: {str(e)}")
