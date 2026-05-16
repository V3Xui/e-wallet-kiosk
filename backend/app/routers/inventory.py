from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.database import get_db
from app.models.inventory import Inventory

router = APIRouter(prefix="/inventory", tags=["Inventory"])

class RefillRequest(BaseModel):
    bill_100: int
    bill_50: int
    coin_20: int
    action: str = "add"

@router.get("/")
def get_inventory(db: Session = Depends(get_db)):
    inv = db.query(Inventory).filter(Inventory.id == 1).first()
    
    # THE FIX: If the vault doesn't exist yet, automatically create it!
    if not inv:
        inv = Inventory(id=1, bill_100=0, bill_50=0, coin_20=0)
        db.add(inv)
        db.commit()
        db.refresh(inv)
    
    total_value = (inv.bill_100 * 100) + (inv.bill_50 * 50) + (inv.coin_20 * 20)
    
    return {
        "bill_100": inv.bill_100,
        "bill_50": inv.bill_50,
        "coin_20": inv.coin_20,
        "total_value": total_value,
        "last_updated": inv.last_updated
    }

@router.put("/refill")
def refill_inventory(data: RefillRequest, db: Session = Depends(get_db)):
    inv = db.query(Inventory).filter(Inventory.id == 1).first()
    
    if not inv:
        inv = Inventory(id=1, bill_100=0, bill_50=0, coin_20=0)
        db.add(inv)
    
    # THE FIX: Check what button the admin clicked!
    if data.action == "set":
        # Overwrite the database with the exact corrected numbers
        inv.bill_100 = data.bill_100
        inv.bill_50 = data.bill_50
        inv.coin_20 = data.coin_20
        msg = "Inventory corrected successfully!"
    else:
        # Standard refill: add to existing stock
        inv.bill_100 += data.bill_100
        inv.bill_50 += data.bill_50
        inv.coin_20 += data.coin_20
        msg = "Stock added successfully!"
    
    db.commit()
    return {"status": "success", "message": msg}