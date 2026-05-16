from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import transaction
from app.routers import inventory  # It is best practice to keep imports at the top

from app.database.database import engine, Base
from app.models.transaction import Transaction
from app.models.inventory import Inventory

# Create the tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

#Allow your frontend to talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transaction.router)
app.include_router(inventory.router)