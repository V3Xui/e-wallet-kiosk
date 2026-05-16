import requests
import os
from dotenv import load_dotenv

load_dotenv()
# Use the same secret key you used for the kiosk
AUTH = (os.getenv("PAYMONGO_SECRET_KEY"), '')

def force_refund(payment_id):
    url = "https://api.paymongo.com/v1/refunds"
    
    payload = {
        "data": {
            "attributes": {
                "amount": 10000, # ₱100.00 in cents
                "payment_id": payment_id,
                "reason": "others",
                "notes": "Testing refund because the dashboard button is missing"
            }
        }
    }
    
    response = requests.post(url, json=payload, auth=AUTH)
    
    if response.status_code == 200:
        print("✅ Refund Successful! Check your dashboard now.")
    else:
        print(f"❌ Failed: {response.text}")

# Replace this with the ID from your last screenshot
force_refund("pay_i83eApfL9Brxjmp96PqLz7Yx")