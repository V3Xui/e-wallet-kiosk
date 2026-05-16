from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database.database import Base
from datetime import datetime

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending") 
    paymongo_intent_id = Column(String, unique=True, index=True)
    qr_data = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)