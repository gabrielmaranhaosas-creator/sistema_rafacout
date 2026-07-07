from pydantic import BaseModel

class WhatsAppMessage(BaseModel):
    wa_id: str
    text: str
    name: str