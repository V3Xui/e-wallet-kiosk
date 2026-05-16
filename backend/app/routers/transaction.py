import os
import hmac
import hashlib
from app.config import settings
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.database import get_db, SessionLocal
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.paymongo import create_qrph_payment, get_payment_intent_status, cancel_payment_intent
from app.services.dispenser import calculate_bills
from app.models.inventory import Inventory

router = APIRouter(prefix="/transactions", tags=["Transactions"])
WEBHOOK_SECRET = os.getenv("PAYMONGO_WEBHOOK_SECRET")

@router.post("/webhook")
async def paymongo_webhook(request: Request):
    # 1. Grab the raw data and the security header
    raw_body = await request.body()
    signature_header = request.headers.get("Paymongo-Signature")

    # 2. Verify the Signature
    if WEBHOOK_SECRET and signature_header:
        try:
            # PayMongo's header looks like: t=161...,te=test_sig,li=live_sig
            sig_parts = dict(part.split("=", 1) for part in signature_header.split(","))
            timestamp = sig_parts.get("t")
            
            # Check 'te' for test mode, 'li' for live mode
            incoming_sig = sig_parts.get("te") if "te" in sig_parts else sig_parts.get("li")

            # Recreate the signature string
            signed_payload = f"{timestamp}.{raw_body.decode('utf-8')}"
            
            # Hash it using our secret key
            expected_sig = hmac.new(
                WEBHOOK_SECRET.encode('utf-8'),
                signed_payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            # Compare them safely
            if not hmac.compare_digest(expected_sig, incoming_sig):
                print("❌ SECURITY ALERT: Fake webhook blocked!")
                raise HTTPException(status_code=400, detail="Invalid signature")
                
        except HTTPException:
            raise
        except Exception as e:
            print("❌ Signature parsing failed:", e)
            raise HTTPException(status_code=400, detail="Signature error")

    # 3. Parse JSON safely inside the try-block
    try:
        # Prevent 500 error if someone sends an empty ping (like the FastAPI docs)
        if not raw_body:
            return {"status": "ignored", "detail": "Empty body"}

        payload = await request.json()
        event_type = payload.get("data", {}).get("attributes", {}).get("type")
        
        if event_type == "checkout_session.payment.paid":
            session_data = payload["data"]["attributes"]["data"]
            session_id = session_data.get("id")
            
            if session_id:
                db = SessionLocal()
                try:
                    tx = db.query(Transaction).filter(
                        Transaction.paymongo_intent_id == session_id
                    ).first()
                    
                    if tx and tx.status != "paid":
                        tx.status = "paid"
                        
                        # Trigger the Smart Matrix
                        h100, f50, t20 = calculate_bills(int(tx.amount))
                        
                        # Deduct from inventory
                        inv = db.query(Inventory).filter(Inventory.id == 1).first()
                        if inv:
                            inv.bill_100 -= h100
                            inv.bill_50 -= f50
                            inv.coin_20 -= t20
                        
                        db.commit()
                        
                        # Hardware Execution Log
                        print(f"✅ Webhook Success: Transaction {tx.id} marked as PAID.")
                        print(f"💰 DISPENSING: {h100}x₱100, {f50}x₱50, {t20}x₱20")
                        print(f"📊 INVENTORY LEFT: {inv.bill_100}x₱100, {inv.bill_50}x₱50, {inv.coin_20}x₱20")
                finally:
                    db.close()
                    
    except Exception as e:
        print(f"❌ Webhook Processing Error: {str(e)}")
        
    return {"status": "received"}

@router.post("/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    # Updated limits: ₱20 minimum and ₱300 maximum supported by Checkout Sessions
    if transaction.amount < 20 or transaction.amount > 300:
        raise HTTPException(status_code=400, detail="Amount must be between ₱20 and ₱300.")
    
    # NEW: The Auto-Lock Check
    h100, f50, t20 = calculate_bills(int(transaction.amount))
    
    # Check if we have the exact bills needed
    inv = db.query(Inventory).filter(Inventory.id == 1).first()
    if not inv:
        raise HTTPException(status_code=500, detail="Inventory uninitialized.")
        
    if inv.bill_100 < h100 or inv.bill_50 < f50 or inv.coin_20 < t20:
        # This will trigger the showCustomAlert() on your frontend automatically!
        raise HTTPException(status_code=500, detail="Inventory uninitialized.")
        
    paymongo_data = create_qrph_payment(transaction.amount)
    if "error" in paymongo_data:
        raise HTTPException(status_code=400, detail=paymongo_data["error"])

    # This creates the object with the CORRECT names from models/transaction.py
    new_tx = Transaction(
        amount=transaction.amount,
        paymongo_intent_id=paymongo_data["intent_id"],
        qr_data=paymongo_data["qr_data"],
        status="pending"
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    return new_tx

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx: raise HTTPException(status_code=404, detail="Not found")
    
    # THE FIX: Added "active" to the list so polling doesn't give up!
    active_statuses = ["pending", "unpaid", "awaiting_payment_method", "awaiting_next_action", "processing", "active"]
    
    if tx.status in active_statuses and tx.paymongo_intent_id:
        live_status = get_payment_intent_status(tx.paymongo_intent_id)
        if live_status and live_status != tx.status:
            tx.status = live_status
            db.commit()
            db.refresh(tx)
    return tx

@router.put("/{transaction_id}/cancel", response_model=TransactionResponse)
def cancel_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx: raise HTTPException(status_code=404, detail="Not found")
    
    if tx.status in ["pending", "unpaid"]:
        tx.status = "cancelled"
        db.commit()
        db.refresh(tx)
        if tx.paymongo_intent_id:
            cancel_payment_intent(tx.paymongo_intent_id)
    return tx