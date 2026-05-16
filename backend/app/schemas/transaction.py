from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TransactionCreate(BaseModel):
    amount: float

class TransactionResponse(BaseModel):
    id: int
    amount: float
    status: str
    paymongo_intent_id: Optional[str] = None # Match database
    qr_data: Optional[str] = None            # Match database
    created_at: datetime

    class Config:
        from_attributes = True