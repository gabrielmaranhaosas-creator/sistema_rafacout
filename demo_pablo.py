import streamlit as st
from groq import Groq
import os
import json
import sqlite3
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
    
    DB_PATH = "banco_de_dados_leads.db"

# ======================================================================
# 1.5 CAMADA DE PERSISTÊNCIA (Repository Pattern c/ SQLite)
# ======================================================================
class LeadRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leads (
                    telefone TEXT PRIMARY KEY,
                    estado_fsm_json TEXT,
                    chat_history_json TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def get_lead(self, telefone: str) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT estado_fsm_json, chat_history_json FROM leads WHERE telefone = ?", (telefone,))
            row = cursor.fetchone()
            
            estado_padrao = {
                "ja_se_apresentou": False, "pre_proposta_enviada": False, "proposta_enviada": False,
                "nome_cliente": None, "tipo_evento": None, "data": None, 
                "cidade": None, "casa_festas": None, "horario_show": None, "nome_homenageado": None,
                "local_perguntado": False, "horario_perguntado": False
            }
            chat_padrao = []
            
            if row:
                estado_db = json.loads(row[0]) if row[0] else {}
                chat_db = json.loads(row[1]) if row[1] else chat_padrao
                estado_mesclado = {**estado_padrao, **estado_db}
                return {"memoria_lead": estado_mesclado, "chat_history": chat_db}
            
            return {"memoria_lead": estado_padrao, "chat_history": chat_padrao}

    def save_lead(self, telefone: str, memoria_lead: dict, chat_history: list):
        estado_json = json.dumps(memoria_lead, ensure_ascii=False)
        chat_json = json.dumps(chat_history, ensure_ascii=False)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO leads (telefone, estado_fsm_json, chat_history_json, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(telefone) DO UPDATE SET 
                    estado_fsm_json = excluded.estado_fsm_json,
                    chat_history_json = excluded.chat_history_json,
                    updated_at = CURRENT_TIMESTAMP
            ''', (telefone, estado_json, chat_json))
            conn.commit()

    def delete_lead(self, telefone: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM leads WHERE telefone = ?", (telefone,))
            conn.commit()

# ======================================================================
# 2. CAMADA DE NEGÓCIOS: ROTEIROS EXATOS DO DOCUMENTO
# ======================================================================
class RoteirosPablo:
    SAUDACAO_SIMPLES = "{saudacao_tempo}{nome_cliente}! Meu nome é Pablo e sou o empresário de Rafa, tudo bem!? Obrigado pelo contato e interesse. Em que posso ajudar?"
    ORCAMENTO_SEM_DADOS_NOVO = "{saudacao_tempo}{nome_cliente}! Aqui é o Pablo, empresário de Rafa Cout, tudo bem?! Obrigado pelo contato. Para confirmar a disponibilidade e passar a proposta, eu preciso de algumas informações: Tipo do evento (Casamento, Aniversário...), Data, Local e Horário previsto para o show. Consegue me passar?"
    PARCIAL_NOVO = "{saudacao_tempo}{nome_cliente}! Aqui é o Pablo, empresário de Rafa Cout, tudo bem?! Obrigado pelo contato. Para confirmar a disponibilidade e passar a proposta, eu preciso complementar algumas informações: {campos_faltantes}. Consegue me passar?"
    PARCIAL_CONTINUACAO = "Para confirmar a disponibilidade e passar a proposta, eu preciso complementar algumas informações: {campos_faltantes}. Consegue me passar?"
    CONFIRMA_HORARIO = "Para confirmar a disponibilidade, o horário que você me informou é de início da festa ou de início do nosso show? 😊"
    CONFIRMA_LOCAL = "Pode me confirmar o local exato (nome do espaço ou casa de festas) do evento? 😃"
    CONFIRMA_CORP_SEM_EMPRESA = "Pode me informar o nome da empresa e do evento para que eu possa colocar corretamente na proposta e em nossa agenda?"
    CONFIRMA_CASAMENTO = "Pode me informar o nome do casal para que eu possa colocar corretamente na proposta e em nossa agenda?"
    CONFIRMA_ANIVERSARIO = "Pode me informar o nome do/da aniversariante que eu possa colocar corretamente na proposta e em nossa agenda?"
    PRE_PROPOSTA = "Enquanto monto a proposta, deixa te perguntar: você já conhece o show de Rafa? Rafa tem um repertório bem abrangente, podendo \"passear\" por várias estilos (sertanejo, forró, axé, pagode, swingueira etc.). Nossa proposta é ser aquela banda que anima a pista ou mantém ela com a energia lá em cima. Posso mandar uma lista de repertório para vocês terem uma ideia e, caso fechem, podemos marcar uma reunião para falar especificamente sobre esse tema"
    PONTE_CONVERSACIONAL = "Perfeito! Vou separar alguns materiais nossos para te enviar, assim vocês conseguem sentir um pouco mais da nossa energia. 🎶\n\nE conforme conversamos, "
    PROPOSTA_PADRAO = "{saudacao_proposta}segue a proposta para a realização do show de Rafa no {evento}, no dia *{data_horario}, no {local}.*\n\n*[📎 ARQUIVO PDF ANEXADO: Proposta_Rafa_Cout.pdf]*\n\nMais uma vez agradecemos o interesse e espero podermos levar a energia de Rafa para esse dia tão especial.😃\n\nQualquer dúvida ou ajuda, estou à disposição. Fico no seu aguardo.😊"

# ======================================================================
# 3. CAMADA DE INFRAESTRUTURA NLU & NLG (Cérebro Híbrido)
# ======================================================================
class AIEngine:
    EXTRACTION_PROMPT = """
    Você é um extrator de dados JSON estrito. Leia o histórico da conversa.
    NÃO gere texto. Responda APENAS em JSON válido.

    REGRAS CRÍTICAS DE EXTRAÇÃO:
    - "tipo_evento": Exija a natureza EXATA. DEVE ser: Casamento, Corporativo, Aniversário, 15 Anos, Formatura, ou Evento Público. Se o cliente disser palavras genéricas, CLASSIFIQUE COMO null.
    - "data": Formato natural (ex: "19 de dezembro de 2026").
    - "cidade": Apenas o nome da cidade.
    - "casa_festas": O nome do espaço. Se o cliente falar APENAS a cidade, classifique isso como null.
    - "horario_show": Formato natural (ex: "22 horas").
    - "nome_homenageado": Nome do casal/aniversariante/empresa.
    - "nome_cliente": NUNCA preencha "Pablo" ou "Rafa" aqui.

    FORMATO DE SAÍDA OBRIGATÓRIO:
    {
        "intencao": "oi_simples | orcamento | informacao",
        "entidades": {
            "nome_cliente": "valor ou null", "tipo_evento": "Casamento | Corporativo | Aniversário | Formatura | 15 Anos | null",
            "data": "valor ou null", "cidade": "valor ou null", "casa_festas": "valor ou null",
            "horario_show": "valor ou null", "nome_homenageado": "valor ou null"
        }
    }
    """
    
    POS_PROPOSTA_PROMPT = """
    Você é Pablo, o empresário atencioso e persuasivo do cantor Rafa Cout.
    Você acabou de enviar um orçamento em PDF pelo WhatsApp para este cliente.
    O cliente está conversando com você APÓS receber o orçamento.

    BASE DE CONHECIMENTO (VALORES E PACOTES):
    - O formato do show do Rafa Cout é extremamente animado, com repertório eclético (sertanejo, axé, forró, pagode).
    - Valor Base (Apenas a Banda): R$ 8.000,00.
    - Valor Completo Casamento/Corporativo (Banda + Som + Luz): R$ 12.000,00.
    - Forma de Pagamento: 50% na assinatura do contrato para bloqueio da data, e 50% até a semana do evento.

    REGRAS DE CONVERSAÇÃO DINÂMICA:
    1. AWARENESS DE HISTÓRICO: Leia as últimas mensagens. SE VOCÊ JÁ DISSE UMA COISA, NUNCA REPITA A MESMA FRASE. Mude as palavras, avance a conversa.
    2. SE O CLIENTE PEDIR O PREÇO OU NÃO ABRIR O PDF: Não se faça de rogado. Passe o valor imediatamente de forma clara, amigável e vendedora. Ex: "Sem problema! O valor do nosso pacote completo fica em..."
    3. NEGOCIAÇÃO: Defenda o valor da entrega do Rafa. Mostre que é um investimento na energia da festa.
    4. Seja conciso. É o WhatsApp, não escreva textões.
    """

    def __init__(self):
        self.client = Groq(api_key=Config.get_groq_key())

    def analisar_mensagem(self, historico: list) -> dict:
        messages = [{"role": "system", "content": self.EXTRACTION_PROMPT}] + historico
        try:
            response = self.client.chat.completions.create(
                messages=messages, model="llama-3.3-70b-versatile",
                temperature=0.0, response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {"intencao": "informacao", "entidades": {}}

    def gerar_resposta_pos_proposta(self, historico: list) -> str:
        messages = [{"role": "system", "content": self.POS_PROPOSTA_PROMPT}] + historico
        try:
            response = self.client.chat.completions.create(
                messages=messages, model="llama-3.3-70b-versatile",
                temperature=0.4, max_tokens=250
            )
            return response.choices[0].message.content
        except Exception:
            return "Deixa eu verificar isso para você rapidinho! Pode aguardar um instante? 😊"

# ======================================================================
# 4. MÁQUINA DE ESTADOS FINITA (O Cérebro em Python)
# ======================================================================
class PabloFSM:
    def __init__(self, ai_engine: AIEngine):
        self.ai = ai_engine

    def processar_estado(self, intencao: str, entidades: dict, memoria: dict, historico: list) -> str:
        for k, v in entidades.items():
            if v and str(v).lower() not in ["null", "none"]: memoria[k] = v

        nome_raw = memoria.get("nome_cliente")
        if nome_raw and str(nome_raw).strip().lower() in ["pablo", "rafa", "rafa cout"]:
            nome_raw = None; memoria["nome_cliente"] = None
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

        # GERAÇÃO IA PÓS-PROPOSTA (Dinâmica e com Contexto de Preço)
        if memoria.get("proposta_enviada"):
            return self.ai.gerar_resposta_pos_proposta(historico)

        if memoria.get("pre_proposta_enviada"):
            memoria["proposta_enviada"] = True
            evento_raw = memoria.get("tipo_evento", "evento")
            evento = str(evento_raw).strip().title() if evento_raw else "evento"
            data = str(memoria.get("data", "")).strip()
            horario = str(memoria.get("horario_show", "")).strip()
            
            cidade_str = str(memoria.get("cidade", "")).strip().title()
            casa_str = str(memoria.get("casa_festas", "")).strip().title()
            local_final = f"{casa_str}, {cidade_str}".strip(" ,") if casa_str else cidade_str
            
            proposta_texto = RoteirosPablo.PROPOSTA_PADRAO.format(
                saudacao_proposta=saudacao_proposta, evento=evento,
                data_horario=f"{data} às {horario}", local=local_final
            )
            return RoteirosPablo.PONTE_CONVERSACIONAL + proposta_texto

        if intencao == "oi_simples" and not memoria.get("ja_se_apresentou"):
            memoria["ja_se_apresentou"] = True
            return RoteirosPablo.SAUDACAO_SIMPLES.format(saudacao_tempo=saudacao_tempo, nome_cliente=tratamento_nome).replace(" .", ".")

        campos_faltantes = []
        if not memoria.get("tipo_evento"): campos_faltantes.append("Tipo exato do evento (Ex: Casamento, Aniversário, Corporativo)")
        if not memoria.get("data"): campos_faltantes.append("Data completa (com ano)")
        if not memoria.get("cidade") and not memoria.get("casa_festas"): campos_faltantes.append("Local (Cidade e Casa de Festas)")
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

        if memoria.get("cidade") and not memoria.get("casa_festas"):
            if not memoria.get("local_perguntado"):
                memoria["local_perguntado"] = True
                return RoteirosPablo.CONFIRMA_LOCAL
                
        if not memoria.get("horario_perguntado"):
            horario_str = str(memoria.get("horario_show")).lower()
            is_madrugada = any(m in horario_str for m in ["madrugada", "00:", "01:", "02:", "03:", "04:", "1 ", "2 "])
            memoria["horario_perguntado"] = True
            if not is_madrugada:
                return RoteirosPablo.CONFIRMA_HORARIO

        tipo = str(memoria.get("tipo_evento") or "").lower()
        if not memoria.get("nome_homenageado"):
            if "casamento" in tipo: return RoteirosPablo.CONFIRMA_CASAMENTO
            elif "anivers" in tipo or "15 anos" in tipo: return RoteirosPablo.CONFIRMA_ANIVERSARIO
            elif "corporativo" in tipo or "confrat" in tipo: return RoteirosPablo.CONFIRMA_CORP_SEM_EMPRESA

        memoria["pre_proposta_enviada"] = True
        return RoteirosPablo.PRE_PROPOSTA

# ======================================================================
# 5. RENDERIZAÇÃO DA INTERFACE & INJEÇÃO DE BANCO DE DADOS
# ======================================================================
db = LeadRepository(Config.DB_PATH)

st.sidebar.markdown("### 📱 Simulador de WhatsApp")
st.sidebar.caption("O sistema agora isola as conversas usando um ID único de telefone armazenado em SQLite.")
numero_lead = st.sidebar.text_input("Número do Lead (ex: 55819999999)", value="5581999999999")

if st.sidebar.button("🗑️ Apagar Sessão Deste Número", type="primary"):
    db.delete_lead(numero_lead)
    st.sidebar.success("Memória apagada! Recarregue a página.")
    st.stop()

dados_do_banco = db.get_lead(numero_lead)
memoria_lead = dados_do_banco["memoria_lead"]
chat_history = dados_do_banco["chat_history"]

col_chat, col_debug = st.columns([2, 1])

with col_chat:
    st.title("📱 Atendimento Oficial - Rafa Cout [BUILD V11 - Cérebro Híbrido Liberto]")
    st.caption(f"A conversar com: `{numero_lead}` (Dados persistidos no SQLite)")

    ai = AIEngine()
    fsm = PabloFSM(ai)

    for msg in chat_history:
        avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Mensagem do cliente..."):
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
        chat_history.append({"role": "user", "content": prompt})
        
        db.save_lead(numero_lead, memoria_lead, chat_history)

        with st.spinner("Processando Inteligência Híbrida (Triagem ou Conversação)..."):
            analise_json = ai.analisar_mensagem(chat_history)
            resposta_oficial = fsm.processar_estado(
                intencao=analise_json.get("intencao", "informacao"),
                entidades=analise_json.get("entidades", {}),
                memoria=memoria_lead,
                historico=chat_history
            )

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(resposta_oficial)
        chat_history.append({"role": "assistant", "content": resposta_oficial})

        db.save_lead(numero_lead, memoria_lead, chat_history)
        st.rerun()

with col_debug:
    st.markdown("### 💾 Base de Dados (SQLite)")
    st.caption("Estado em Tempo Real da Memória FSM")
    st.json(memoria_lead)