import requests
from app.config import settings

# Authenticate using the centralized settings token
# PayMongo uses basic auth with the secret key as the username and an empty password
AUTH = (settings.PAYMONGO_SECRET_KEY, '')

def create_qrph_payment(amount: float, description: str = "Kiosk Cashout"):
    """
    Creates a PayMongo Hosted Checkout Session. 
    Returns a session ID and a checkout URL supporting QR Ph, GCash, and Maya.
    """
    url = "https://api.paymongo.com/v1/checkout_sessions"
    amount_in_cents = int(amount * 100)

    payload = {
        "data": {
            "attributes": {
                "send_email_receipt": True,
                "show_description": True,
                "payment_method_types": ["qrph", "gcash", "paymaya"],
                "line_items": [
                    {
                        "currency": "PHP",
                        "amount": amount_in_cents,
                        "description": description,
                        "name": "Kiosk Cashout Request",
                        "quantity": 1
                    }
                ]
            }
        }
    }

    response = requests.post(url, json=payload, auth=AUTH)
    
    if response.status_code == 200:
        data = response.json()["data"]
        return {
            "intent_id": data["id"],
            "qr_data": data["attributes"]["checkout_url"] 
        }

    return {"error": f"Session Error: {response.text}"}


def get_payment_intent_status(session_id: str):
    """Checks the live payment status of the hosted checkout session."""
    url = f"https://api.paymongo.com/v1/checkout_sessions/{session_id}"
    response = requests.get(url, auth=AUTH)
    
    if response.status_code == 200:
        status = response.json()["data"]["attributes"]["status"]
        return "paid" if status == "paid" else status 
    return None


def cancel_payment_intent(session_id: str):
    """Expires an active checkout session before completion."""
    url = f"https://api.paymongo.com/v1/checkout_sessions/{session_id}/expire"
    response = requests.post(url, auth=AUTH)
    return response.status_code == 200