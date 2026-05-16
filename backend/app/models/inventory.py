from sqlalchemy import Column, Integer, DateTime
from app.database.database import Base
from datetime import datetime

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    bill_100 = Column(Integer, default=0)
    bill_50 = Column(Integer, default=0)
    coin_20 = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)