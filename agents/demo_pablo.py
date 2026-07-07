import streamlit as st
from groq import Groq
import os

# ==========================================
# 1. CONFIGURAÇÃO DA INTERFACE WEB (UI/UX)
# ==========================================
st.set_page_config(
    page_title="Motor Pablo - Prova Real", 
    page_icon="🤖", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("📱 Atendimento Simulado - Rafa Cout")
st.caption("Ambiente de testes com o Cérebro Avançado. Tente 'quebrar' o robô mandando informações parciais.")
st.divider()

# ==========================================
# 2. INICIALIZAÇÃO DO MOTOR E SEGURANÇA
# ==========================================
@st.cache_resource
def iniciar_cliente_groq():
    """Inicializa o cliente da API de forma segura e com cache para performance."""
    chave = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
    if not chave:
        st.error("🚨 Falha de Autenticação: A chave GROQ_API_KEY não foi encontrada nos Secrets.")
        st.stop()
    return Groq(api_key=chave)

client = iniciar_cliente_groq()

# ==========================================
# 3. CORE COGNITIVO (O CÉREBRO BLINDADO)
# ==========================================
SYSTEM_PROMPT = """
Você é Pablo Bezerra, empresário exclusivo do cantor Rafa Cout. 
Você está conversando no WhatsApp com um cliente interessado em contratar o show.

# 1. IDENTIDADE E TOM DE VOZ
- Seu tom é educado, profissional, direto e genuinamente acolhedor.
- Use sutil e inteligentemente emojis leves (como 😊 e 😃).
- Fale de forma totalmente natural e fluida.

# 2. REGRAS DE MEMÓRIA E ANTI-LOOP (CRÍTICO)
- ANALISE O HISTÓRICO DA CONVERSA: Nunca repita a saudação ("Olá, aqui é o Pablo...") se você já se apresentou antes. Continue a conversa do ponto em que parou.
- RECONHEÇA DADOS PARCIAIS: Se o cliente der um dado incompleto (ex: "Novembro de 2026"), reconheça a informação e peça apenas o complemento (ex: "o dia exato") junto com o que mais faltar. Nunca ignore o que o cliente já digitou.
- FAÇA APENAS UMA PERGUNTA POR VEZ.

# 3. OBJETIVO DE TRIAGEM COMERCIAL
Saber 4 informações essenciais:
1. Nome/Tipo do evento (Casamento, Corporativo, Aniversário, 15 anos, etc.).
2. Data exata (dia, mês e ano).
3. Local (Cidade e casa de festas).
4. Horário previsto para o início do show.

# 4. ROTEIROS DE RESPOSTA (USE EXATAMENTE ESTAS ESTRUTURAS)

## SITUAÇÃO A: Cliente enviou "Oi" sem nenhuma informação
- "Boa tarde [NOME DO CLIENTE]. Meu nome é Pablo e sou o empresário de Rafa, tudo bem!? Obrigado pelo contato e interesse. Em que posso ajudar? 😊".

## SITUAÇÃO B: Cliente pediu orçamento, mas faltam informações
- Se for o primeiro contato da conversa: "Olá, [NOME DO CLIENTE]. Aqui é o Pablo, empresário de Rafa Cout, tudo bem?! Obrigado pelo contato. Para confirmar a disponibilidade e passar a proposta, eu preciso complementar algumas informações: [INSERIR APENAS AS INFORMAÇÕES QUE FALTAM]. Consegue me passar? 😃".
- Se a data informada não tiver o ano, peça a confirmação se é para o ano corrente.

## SITUAÇÃO C: Refinamento de Dados (Confirmações Finais)
Mesmo com as informações preenchidas, faça as seguintes confirmações se necessário:
- Horário: "Para confirmar a disponibilidade, o horário que você me informou é de início da festa ou de início do nosso show? 😊".
- Local: "Pode me confirmar o local exato (nome da casa de festas) do evento? 😃".
- Corporativo (sem empresa): "Pode me informar o nome da empresa e do evento para que eu possa colocar corretamente na proposta e em nossa agenda? 😊".
- Casamento: "Pode me informar o nome do casal para que eu possa colocar corretamente na proposta e em nossa agenda? 😃".
- Aniversário: "Pode me informar o nome do(a) aniversariante que eu possa colocar corretamente na proposta e em nossa agenda? 😊".

## SITUAÇÃO D: Todas as informações completas (Gatilho da Pré-Proposta)
Quando não faltar mais nada, envie EXATAMENTE:
"Enquanto monto a proposta, deixa te perguntar: você já conhece o show de Rafa? Rafa tem um repertório bem abrangente, podendo 'passear' por várias estilos (sertanejo, forró, axé, pagode, swingueira etc.). Nossa proposta é ser aquela banda que anima a pista ou mantém ela com a energia lá em cima. Posso mandar uma lista de repertório para vocês terem uma ideia e, caso fechem, podemos marcar uma reunião para falar especificamente sobre esse tema 😊".

# 5. DIRETRIZES DE SEGURANÇA E LIMITES
- PROIBIDO inventar valores de cachê ou descontos.
- NUNCA envie a proposta final com preços por aqui. O seu objetivo termina ao enviar a mensagem da SITUAÇÃO D.

# 6. PROTOCOLO DE EXTRACÃO DE TAGS (DEBUG DO SISTEMA)
No final da sua resposta, deixe duas linhas em branco e adicione as tags abaixo com o que você já sabe da conversa. Use 'Não informado' para dados pendentes.
[TIPO_EVENTO: valor]
[DATA: valor]
[LOCAL: valor]
[HORARIO: valor]
"""

# ==========================================
# 4. GERENCIAMENTO AVANÇADO DE ESTADO
# ==========================================
if "messages" not in st.session_state:
    # Inicializa a memória da IA com a instrução do sistema
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Renderiza o histórico de chat na tela (ignorando o prompt do sistema)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        avatar_icon = "🧑‍💻" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.markdown(msg["content"])

# ==========================================
# 5. MOTOR DE INFERÊNCIA (I/O)
# ==========================================
if prompt := st.chat_input("Escreva sua mensagem simulando o cliente..."):
    
    # 1. Exibe a mensagem do usuário
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    
    # 2. Persiste na memória da sessão
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 3. Chama a Groq API com tratamento de erros de rede
    try:
        with st.spinner("O Cérebro está processando..."):
            chat_completion = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
                temperature=0.2, # Mantido baixo para seguir o script à risca
                max_tokens=1024
            )
            
        resposta_ia = chat_completion.choices[0].message.content
        
        # 4. Exibe a resposta do Pablo
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(resposta_ia)
            
        # 5. Persiste a resposta na memória para contexto futuro
        st.session_state.messages.append({"role": "assistant", "content": resposta_ia})
        
    except Exception as e:
        st.error(f"Erro Crítico de Conexão com a Groq API: {str(e)}")
        st.info("Verifique se a API Key é válida e se não há bloqueios de rede.")
