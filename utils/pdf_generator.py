from fpdf import FPDF
import os

class PropostaPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "PROPOSTA COMERCIAL - RAFA COUT", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")

def gerar_pdf_proposta(lead: dict, preco_especial: str = "R$ 13.000,00") -> str:
    pdf = PropostaPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Dados tratados (Sua lógica de limpeza profissional)
    nome_cliente = str(lead.get('name', 'Cliente')).strip()
    evento = str(lead.get('event_type', 'Não informado')).strip()
    data_ev = str(lead.get('event_date', 'Não informado')).strip()
    local_ev = str(lead.get('location', 'Não informado')).strip()
    hora_ev = str(lead.get('event_time', 'Não informado')).strip()

    # Conteúdo
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Olá, {nome_cliente}!", 0, 1)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "É um prazer apresentar o orçamento para o seu evento. Seguem os detalhes confirmados:")
    pdf.ln(5)
    
    # Tabela (Seu layout profissional)
    pdf.set_fill_color(240, 240, 240)
    campos = [("Evento:", evento), ("Data:", data_ev), ("Local:", local_ev), ("Horário:", hora_ev)]
    for label, valor in campos:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(40, 10, label, 1, 0, "L", True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f" {valor}", 1, 1)

    pdf.ln(10)
    
    # Proposta Financeira (Lógica Dinâmica)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "PROPOSTA FINANCEIRA", 0, 1)
    pdf.set_font("Arial", "", 12)
    
    pdf.cell(40, 10, "Cachê Padrão:", 0, 0)
    pdf.set_text_color(150, 0, 0)
    pdf.cell(0, 10, "R$ 15.000,00", 0, 1)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(45, 10, "Condição Especial:", 0, 0)
    pdf.set_text_color(0, 128, 0)
    pdf.cell(0, 10, f"{preco_especial} (Fechamento Imediato)", 0, 1)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    pdf.multi_cell(0, 10, "Aguardamos sua aprovação no WhatsApp para o envio do checklist de contrato e do rider técnico.")
    
    # Caminhos (Sua estrutura robusta)
    diretorio_atual = os.path.abspath(os.getcwd())
    pasta_propostas = os.path.join(diretorio_atual, "propostas")
    if not os.path.exists(pasta_propostas):
        os.makedirs(pasta_propostas)

    wa_id_seguro = str(lead.get('wa_id', '000')).strip().replace('\n', '').replace('\r', '')
    caminho_completo = f"{pasta_propostas}/proposta_{wa_id_seguro}.pdf".replace('\\', '/')
    
    pdf.output(caminho_completo)
    return caminho_completo