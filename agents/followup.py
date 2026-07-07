import sqlite3
from datetime import datetime, timedelta

def processar_follow_ups():
    conn = sqlite3.connect('sistema_rafacout.db')
    cursor = conn.cursor()
    
    # Critério: Status 'proposta_enviada' e última ação há mais de 10 dias
    data_limite = (datetime.now() - timedelta(days=10)).isoformat()
    
    cursor.execute("""
        SELECT wa_id, name, contagem_follow_up FROM leads 
        WHERE status = 'proposta_enviada' AND proposta_enviada_em < ?
    """, (data_limite,))
    
    leads_estagnados = cursor.fetchall()
    
    mensagens_pablo = {
        0: "Passando para saber se você conseguiu analisar a nossa proposta. Fico à disposição para qualquer dúvida ou ajuda. 😊",
        1: "Não sei se viu minha última mensagem, mas estou passando novamente para saber se conseguiu analisar a nossa proposta e se tem interesse em seguir com a contratação de Rafa Cout. Fico à disposição caso tenha alguma dúvida. 👍",
        2: "Passando para saber se conseguiu analisar a nossa proposta e se tem interesse em seguir com a contratação de Rafa Cout. Fico à disposição para avançarmos. 🚀"
    }

    for wa_id, name, count in leads_estagnados:
        if count in mensagens_pablo:
            mensagem = f"Olá {name}! {mensagens_pablo[count]}"
            print(f"DEBUG: Enviando Follow-up para {wa_id}: {mensagem}")
            
            # Atualiza banco
            cursor.execute("""
                UPDATE leads SET 
                contagem_follow_up = ?, 
                ultimo_follow_up_em = ? 
                WHERE wa_id = ?
            """, (count + 1, datetime.now().isoformat(), wa_id))
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    processar_follow_ups()