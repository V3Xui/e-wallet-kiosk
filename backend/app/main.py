from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel

from app.routers import transaction
from app.routers import inventory

from app.database.database import engine, Base
from app.models.transaction import Transaction
from app.models.inventory import Inventory

# Create the tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow your frontend to talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transaction.router)
app.include_router(inventory.router)

class PinRequest(BaseModel):
    pin: str

@app.post("/api/verify-pin")
async def verify_admin_pin(request: PinRequest):
    CORRECT_PIN = "68201"
    
    if request.pin == CORRECT_PIN:
        return {"message": "Success"}
    else:
        raise HTTPException(status_code=401, detail="Invalid PIN")


frontend_path = Path(__file__).resolve().parent.parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")