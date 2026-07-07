import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class Orchestrator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def classificar_requisicao(self, texto: str) -> dict:
        prompt = """
        Você é o Router do Sistema RafaCout. A sua única função é classificar a intenção do cliente.

        REGRAS RÍGIDAS DE CLASSIFICAÇÃO:
        - 'novo_orcamento': OBRIGATÓRIO para saudações (Oi), pedidos de preço, mensagens com detalhes de evento (nome de locais, datas, horários, nomes de noivos/empresas) ou mensagens aprovando orçamentos e fechando contratos.
        - 'envio_comprovativo': APENAS para imagens de PIX, recibos bancários ou avisos de transferência.
        - 'duvida_tecnica': APENAS para perguntas complexas sobre Rider Técnico, rider de luz ou mapa de palco. NÃO use isso para locais de evento ou horários de show.

        Mensagem do Cliente: "{texto}"

        Responda APENAS com um objeto JSON neste formato exato:
        {"intent": "string", "confidence": float}
        """
        response = self.client.chat.completions.create(
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": texto}],
            model=self.model,
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return json.loads(response.choices[0].message.content)

orchestrator = Orchestrator()