from app.database.database import Base, engine
from app.models.transaction import Transaction
 
print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)
 
print("Recreating all tables...")
Base.metadata.create_all(bind=engine)
 
print("Done! Database has been reset.")
 