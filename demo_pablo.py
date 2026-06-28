import streamlit as st
from groq import Groq

# ==========================================
# 1. CONFIGURAÇÃO DA INTERFACE WEB
# ==========================================
st.set_page_config(page_title="Motor Pablo - Prova Real", page_icon="🤖")
st.title("📱 Atendimento Simulado - Rafa Cout")
st.caption("Digite suas mensagens abaixo. Tente 'quebrar' o robô mandando informações parciais.")

# ==========================================
# 2. INICIALIZANDO O CÉREBRO
# ==========================================
CHAVE_GROQ = "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"
client = Groq(api_key=CHAVE_GROQ)

SYSTEM_PROMPT = """
Você é Pablo Bezerra, empresário do cantor Rafa Cout.

SEU OBJETIVO: Coletar 4 informações essenciais:
1. Nome/Tipo do evento
2. Data exata
3. Local
4. Horário do show.

REGRAS DE RESPOSTA:
- Se o cliente mandou apenas "Oi/Olá" sem informações: Peça as 4 informações educadamente.
- Se faltar alguma informação: Agradeça e peça APENAS o que falta.
- Se o cliente já enviou TUDO: Diga que vai verificar a disponibilidade na agenda.
- Use um tom educado, profissional e direto.
- É EXPRESSAMENTE PROIBIDO O USO DE EMOJIS. Nunca utilize nenhuma "carinha" ou símbolo gráfico.
- NUNCA invente valores ou disponibilidades.
- SEJA SUCINTO e natural, como uma conversa real de WhatsApp.
"""

# ==========================================
# 3. GERENCIAMENTO DE MEMÓRIA DA SESSÃO
# ==========================================
# Se for a primeira vez abrindo a página, cria a memória do zero
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Desenha na tela todo o histórico de mensagens (escondendo a regra do sistema)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        # Se for usuário, alinha como cliente. Se for assistant, alinha como Pablo.
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ==========================================
# 4. O CAMPO DE DIGITAÇÃO (A MÁGICA)
# ==========================================
if prompt := st.chat_input("Escreva sua mensagem para o Pablo aqui..."):
    
    # 1. Mostra a mensagem do usuário na tela imediatamente
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Guarda a mensagem na memória
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 3. Chama a Groq para pensar na resposta
    try:
        chat_completion = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )
        resposta_ia = chat_completion.choices[0].message.content
        
        # 4. Mostra a resposta do Pablo na tela
        with st.chat_message("assistant"):
            st.markdown(resposta_ia)
            
        # 5. Guarda a resposta na memória para ele não esquecer o que disse
        st.session_state.messages.append({"role": "assistant", "content": resposta_ia})
        
    except Exception as e:
        st.error(f"Erro na conexão com o motor: {e}")