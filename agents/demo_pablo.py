import streamlit as st
from groq import Groq
import os
import json
from typing import List, Dict, Optional
from datetime import datetime

# ======================================================================
# ARQUITETURA LIMPA: CAMADA DE CONFIGURAÇÃO (core/config.py)
# ======================================================================
class Config:
    """Gerenciador central de configurações do sistema."""
    @staticmethod
    def get_groq_key() -> str:
        chave = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
        if not chave:
            st.error("🚨 ERRO ARQUITETURAL: Chave GROQ_API_KEY ausente.")
            st.stop()
        return chave

# ======================================================================
# ARQUITETURA LIMPA: CAMADA DE INFRAESTRUTURA (services/llm_engine.py)
# ======================================================================
class LLMEngine:
    """Isola a lógica de comunicação com o provedor de IA (Groq/Llama-3)."""
    def __init__(self):
        self.client = Groq(api_key=Config.get_groq_key())
        self.model = "llama-3.3-70b-versatile"
    
    def generate_response(self, messages: List[Dict[str, str]], temperature: float = 0.0) -> str:
        """Gera resposta determinística baseada no contexto injetado."""
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=temperature,
                max_tokens=600,
                presence_penalty=0.0,
                frequency_penalty=0.0
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Falha de infraestrutura LLM: {str(e)}")

# ======================================================================
# ARQUITETURA LIMPA: CAMADA DE PROMPTS (prompts/pablo_prompts.py)
# ======================================================================
class PabloPrompts:
    """Repositório de templates de sistema. Prompts modulares."""
    
    BASE_SYSTEM = """
    Você é Pablo Bezerra, empresário do cantor Rafa Cout. 
    Você atua como um sistema determinístico de atendimento.
    
    REGRAS DE FORMATAÇÃO E TOM DE VOZ:
    - Nunca use markdown pesado (negritos excessivos).
    - Mantenha tom polido e conciso.
    - É proibido criar textos longos ou parágrafos motivacionais.
    
    DIRETRIZ DE ESTADO ATUAL:
    {ESTADO_INSTRUCAO}
    """
    
    STATE_GREETING = """
    O cliente iniciou contato agora.
    Sua única tarefa é responder EXATAMENTE: 
    "Boa tarde! Meu nome é Pablo e sou o empresário de Rafa, tudo bem!? Obrigado pelo contato e interesse. Em que posso ajudar? 😊"
    Não adicione mais nada.
    """
    
    STATE_COLLECTING = """
    Você já se apresentou. Faltam informações cruciais para o orçamento.
    INSTRUÇÃO: Peça de forma educada as seguintes informações que faltam: {DADOS_FALTANTES}.
    ESTRUTURA OBRIGATÓRIA: "Para confirmar a disponibilidade e passar a proposta, eu preciso complementar algumas informações: [Liste os dados faltantes aqui]. Consegue me passar? 😃"
    Nunca repita que seu nome é Pablo.
    """
    
    STATE_READY = """
    Todos os dados foram validados.
    INSTRUÇÃO: Envie o gatilho final EXATAMENTE assim:
    "Obrigado por todas as informações! Vou verificar a disponibilidade na nossa agenda para você. Enquanto monto a proposta para verificarmos, deixa te perguntar: você já conhece o show de Rafa? Rafa tem um repertório bem abrangente, podendo 'passear' por várias estilos (sertanejo, forró, axé, pagode, swingueira etc.). Nossa proposta é ser aquela banda que anima a pista ou mantém ela com a energia lá em cima. Posso mandar uma lista de repertório para vocês terem uma ideia e, caso fechem, podemos marcar uma reunião para falar especificamente sobre esse tema? 😊"
    """

# ======================================================================
# ARQUITETURA LIMPA: CAMADA DE NEGÓCIOS (core/fsm.py)
# ======================================================================
class ConversationalFSM:
    """
    Máquina de Estados Finita. O Python controla o fluxo comercial.
    O LLM apenas verbaliza a ordem do Python.
    """
    def __init__(self, chat_history: List[Dict[str, str]]):
        self.history = chat_history
    
    def _has_greeted(self) -> bool:
        """Verifica deterministicamente no histórico se a saudação ocorreu."""
        for msg in self.history:
            if msg["role"] == "assistant" and "Meu nome é Pablo" in msg["content"]:
                return True
        return False
    
    def _analyze_missing_data(self, user_input: str) -> List[str]:
        """
        Simula a extração de entidades estruturadas. 
        Em produção, usaremos chamadas de function_calling do LLM aqui.
        Por ora, assume que faltam dados básicos.
        """
        faltantes = []
        # TODO: Implementar parser de Regex ou Function Calling real para extração
        # Para demonstração da blindagem de loop, forçaremos a coleta.
        if "data" not in user_input.lower(): faltantes.append("Data exata")
        if "local" not in user_input.lower(): faltantes.append("Local do evento")
        return faltantes

    def compute_next_state(self, user_input: str) -> str:
        """Calcula a instrução injetada no LLM baseada na Máquina de Estados."""
        # TRANSICAO 1: Saudação
        if not self._has_greeted():
            return PabloPrompts.STATE_GREETING
        
        # TRANSICAO 2: Coleta de Dados
        missing_data = self._analyze_missing_data(user_input)
        if missing_data:
            return PabloPrompts.STATE_COLLECTING.format(
                DADOS_FALTANTES=", ".join(missing_data)
            )
            
        # TRANSICAO 3: Gatilho Final
        return PabloPrompts.STATE_READY

# ======================================================================
# ARQUITETURA LIMPA: CAMADA DE APRESENTAÇÃO (app/main_streamlit.py)
# ======================================================================
def main():
    st.set_page_config(page_title="Motor V8 FSM - Rafa Cout", page_icon="⚙️", layout="centered")
    st.title("⚙️ FSM Pablo - Engenharia de Software")
    st.caption("Arquitetura Modular: O Python controla, o LLM apenas verbaliza.")
    st.divider()

    # Inicializa serviços
    llm = LLMEngine()

    # Inicializa sessão
    if "history" not in st.session_state:
        st.session_state.history = []

    # Renderiza UI
    for msg in st.session_state.history:
        avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Loop de Eventos
    if prompt := st.chat_input("Input do lead..."):
        # 1. Registra Input
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
        st.session_state.history.append({"role": "user", "content": prompt})

        # 2. Orquestração FSM (O Python pensa)
        fsm = ConversationalFSM(st.session_state.history)
        instrucao_estado_atual = fsm.compute_next_state(prompt)

        # 3. Monta o Prompt Dinâmico
        system_prompt = PabloPrompts.BASE_SYSTEM.format(ESTADO_INSTRUCAO=instrucao_estado_atual)
        api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.history

        # 4. Inferência (O LLM fala)
        try:
            with st.spinner("Processando Máquina de Estados..."):
                resposta = llm.generate_response(api_messages)
            
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(resposta)
                
            st.session_state.history.append({"role": "assistant", "content": resposta})
            
        except RuntimeError as e:
            st.error(str(e))

if __name__ == "__main__":
    main()
