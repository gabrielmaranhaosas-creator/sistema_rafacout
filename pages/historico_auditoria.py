import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Centro de Telemetria V8", layout="wide")

st.title("📊 Centro de Telemetria - Histórico de Auditoria")
st.markdown("Auditoria em tempo real de todas as instâncias de teste e produção.")

# Conexão com o banco de dados (ajuste o caminho se necessário)
DB_PATH = "sistema_rafacout.db"

def carregar_dados():
    conn = sqlite3.connect(DB_PATH)
    # Recupera todos os leads e suas mensagens
    query = """
    SELECT l.wa_id, l.name, m.role, m.message, m.timestamp 
    FROM leads l
    JOIN mensagens m ON l.wa_id = m.wa_id
    ORDER BY m.timestamp DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

try:
    df = carregar_dados()
    
    # Sidebar para filtragem
    st.sidebar.header("Filtros de Auditoria")
    cliente_filtro = st.sidebar.selectbox("Selecionar Cliente/Lead", ["Todos"] + df['name'].unique().tolist())
    
    if cliente_filtro != "Todos":
        df = df[df['name'] == cliente_filtro]
        
    # Visualização
    for wa_id in df['wa_id'].unique():
        cliente_nome = df[df['wa_id'] == wa_id]['name'].iloc[0]
        with st.expander(f"Cliente: {cliente_nome} | ID: {wa_id}"):
            chat_session = df[df['wa_id'] == wa_id]
            for index, row in chat_session.iterrows():
                with st.chat_message(row['role']):
                    st.write(row['message'])
                    st.caption(f"Horário: {row['timestamp']}")

except Exception as e:
    st.error(f"Erro ao carregar o histórico: {e}")
    st.info("Verifique se o servidor está rodando e se o banco de dados existe.")