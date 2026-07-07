import streamlit as st
import sqlite3
import pandas as pd
import os

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Telemetria V8", page_icon="📊", layout="wide")
st.title("📊 Centro de Telemetria - Histórico")
st.caption("Auditoria em tempo real de todas as instâncias de teste e produção.")

DB_PATH = "sistema_rafacout.db"

# ==========================================
# 2. MOTOR DE LEITURA BLINDADO
# ==========================================
def carregar_dados_auditoria():
    """
    Lê os dados do banco SQLite de forma síncrona para o Streamlit.
    Possui travas de segurança para evitar erros se o banco ou tabelas não existirem.
    """
    if not os.path.exists(DB_PATH):
        return None
        
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        
        # Trava de Segurança: Verifica se a tabela chat_history existe antes de buscar
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history';")
        if cursor.fetchone() is None:
            return None # A tabela ainda não foi criada
            
        # Query adaptada para a sua estrutura real (leads + chat_history)
        query = """
        SELECT 
            l.wa_id AS "ID WhatsApp", 
            l.name AS "Nome do Lead", 
            c.role AS "Remetente", 
            c.content AS "Mensagem", 
            c.timestamp AS "Data/Hora"
        FROM leads l
        JOIN chat_history c ON l.wa_id = c.wa_id
        ORDER BY c.timestamp DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
        
    except Exception as e:
        st.error(f"Falha na leitura do banco de dados: {e}")
        return None
    finally:
        conn.close()

# ==========================================
# 3. RENDERIZAÇÃO DO DASHBOARD
# ==========================================
df_historico = carregar_dados_auditoria()

if df_historico is not None and not df_historico.empty:
    # Exibe a tabela bonitona ocupando a tela toda
    st.dataframe(df_historico, use_container_width=True, hide_index=True)
else:
    # Se o banco estiver vazio, mostra um aviso amigável em vez de erro
    st.info("Nenhum histórico de conversa registrado no banco de dados até o momento. Inicie um atendimento para popular a telemetria.")
