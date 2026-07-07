import aiosqlite
from datetime import datetime
import json

DB_PATH = 'sistema_rafacout.db'

async def inicializar_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Tabela de Leads
        await db.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                wa_id TEXT PRIMARY KEY,
                name TEXT,
                event_type TEXT,
                event_date TEXT,
                location TEXT,
                event_time TEXT,
                status TEXT DEFAULT 'triagem',
                proposta_enviada_em TEXT,
                ultimo_follow_up_em TEXT,
                contagem_follow_up INTEGER DEFAULT 0
            )
        ''')
        # Tabela de Histórico de Conversas (Substitui a memória em RAM)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wa_id TEXT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def obter_ou_criar_lead(wa_id: str, name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM leads WHERE wa_id = ?", (wa_id,)) as cursor:
            lead = await cursor.fetchone()
            
        if not lead:
            await db.execute("INSERT INTO leads (wa_id, name) VALUES (?, ?)", (wa_id, name))
            await db.commit()
            async with db.execute("SELECT * FROM leads WHERE wa_id = ?", (wa_id,)) as cursor:
                lead = await cursor.fetchone()
        return lead

async def atualizar_lead(wa_id: str, campo: str, valor: str):
    if not valor or valor.upper() == "NÃO INFORMADO":
        return
    async with aiosqlite.connect(DB_PATH) as db:
        query = f"UPDATE leads SET {campo} = ? WHERE wa_id = ?"
        await db.execute(query, (valor, wa_id))
        await db.commit()

async def definir_proposta_enviada(wa_id: str):
    hoje = datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE leads 
            SET status = 'proposta_enviada', proposta_enviada_em = ? 
            WHERE wa_id = ?
        """, (hoje, wa_id))
        await db.commit()

# --- NOVAS FUNÇÕES PARA MEMÓRIA DE CONVERSA ---

async def salvar_mensagem_historico(wa_id: str, role: str, content: str):
    """Persiste cada interação da IA e do usuário no banco."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO chat_history (wa_id, role, content) VALUES (?, ?, ?)",
            (wa_id, role, content)
        )
        await db.commit()

async def recuperar_historico_chat(wa_id: str, limite: int = 15) -> list:
    """Recupera as últimas mensagens para fornecer contexto à IA."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT role, content FROM chat_history WHERE wa_id = ? ORDER BY id DESC LIMIT ?",
            (wa_id, limite)
        ) as cursor:
            linhas = await cursor.fetchall()
            
    # Retorna na ordem cronológica (do mais antigo pro mais recente)
    historico = [{"role": row[0], "content": row[1]} for row in reversed(linhas)]
    return historico