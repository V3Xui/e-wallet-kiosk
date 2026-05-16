// ============================================================
//  api.js  —  Frontend ↔ Backend bridge
//  Fix log:
//    • Uses checkout_url to generate QR (no qr_data field needed)
//    • receipt uses paymongo_link_id (not paymongo_intent_id)
//    • cancelCurrentTransaction resets cooldown on cancel
//    • All fetch calls include proper error handling
// ============================================================

const API_URL = "http://127.0.0.1:8000";

let pollingInterval = null;
let currentTransactionId = null;
let isProcessingRequest = false;
let lastTransactionTime = 0;
const COOLDOWN_PERIOD = 15000; 

// ─────────────────────────────────────────────
//  STEP 1 — Create transaction & show QR
// ─────────────────────────────────────────────
async function processCashout() {
    if (isProcessingRequest) return;

    const amountInput = document.getElementById("input-amount").value;
    const amount = parseFloat(amountInput);

    // PayMongo Intent API requires a minimum of ₱100, but we allow down to ₱20 for logic
    if (isNaN(amount) || amount < 20 || amount > 300) {
        showCustomAlert("Please enter an amount between ₱20 and ₱300.", "Invalid Amount");
        return;
    }

    // Strictly block the "Impossible Remainder" amounts
    if (amount % 10 !== 0 || amount === 30) {
        showCustomAlert("This amount cannot be dispensed with ₱100, ₱50, and ₱20 bills/coins.", "Hardware Limit");
        return;
    }

    isProcessingRequest = true;

    try {
        // This is the line that defines 'response'!
        const response = await fetch(`${API_URL}/transactions/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ amount })
        });

        if (!response.ok) {
            const errData = await response.json();
            showCustomAlert(errData.detail || "Server rejected request.", `Error (${response.status})`);
            return;
        }

        const data = await response.json();

        // CHANGE: Look for qr_data, not checkout_url
        if (data.qr_data) {
            lastTransactionTime = Date.now();
            currentTransactionId = data.id;

            // This will now receive the 000201... text string
            generateQR(data.qr_data);
            showSection("sec-qr");
            startPollingStatus();

        } else {
            showCustomAlert("No QR data received. Check backend logs.", "API Error");
        }

    } catch (error) {
        console.error("Transaction error:", error);
        showCustomAlert("Cannot reach the server. Ensure FastAPI is running.", "Connection Failed");
    } finally {
        isProcessingRequest = false;
    }
}

// ─────────────────────────────────────────────
//  QR Code generator (Uses the Source of Truth string)
// ─────────────────────────────────────────────
// function generateQR(qrData) {
//     const qrContainer = document.querySelector(".qr-placeholder");
//     qrContainer.innerHTML = ""; // Clear the loading icon
//     const qrImage = document.createElement("img");
//     // THE FIX: Assign the base64 data to the image source
//     // Assuming the backend sends a properly formatted data URI (e.g., "data:image/png;base64,...")
//     qrImage.src = qrData;
//     qrContainer.appendChild(qrImage);
// }

function generateQR(checkoutUrl) {
    const qrContainer = document.querySelector(".qr-placeholder");
    qrContainer.innerHTML = ""; // Clear the old icon
    
    // Draw a new QR code that leads to the PayMongo Authorize page
    new QRCode(qrContainer, {
        text: checkoutUrl,
        width: 250,
        height: 250,
        correctLevel: QRCode.CorrectLevel.H,
    });
}

// ─────────────────────────────────────────────
//  STEP 2 — Poll backend for status
// ─────────────────────────────────────────────
function startPollingStatus() {
    clearInterval(pollingInterval);
    pollingInterval = setInterval(async () => {
        if (!currentTransactionId) return clearInterval(pollingInterval);

        try {
            const res = await fetch(`${API_URL}/transactions/${currentTransactionId}`);
            if (!res.ok) return;

            const txData = await res.json();

            if (txData.status === "paid") {
                clearInterval(pollingInterval);
                showSection("sec-processing");
                setTimeout(() => showReceiptScreen(txData), 2000);
            } else if (["failed", "expired", "cancelled"].includes(txData.status)) {
                clearInterval(pollingInterval);
                showCustomAlert(`Transaction ${txData.status}.`, "Failed");
                showSection("sec-home");
            }
        } catch (e) { console.error("Polling error", e); }
    }, 3000);
}

// ─────────────────────────────────────────────
//  STEP 3 — Receipt screen (Using Intent ID)
// ─────────────────────────────────────────────
function showReceiptScreen(txData) {
    document.getElementById("receipt-amount").innerText = `₱${parseFloat(txData.amount).toFixed(2)}`;
    // Use paymongo_intent_id for the reference number
    document.getElementById("receipt-ref").innerText = txData.paymongo_intent_id || "N/A";
    showSection("sec-receipt");
}

async function cancelCurrentTransaction() {
    clearInterval(pollingInterval);
    showSection("sec-home");
    lastTransactionTime = 0;
    if (!currentTransactionId) return;

    const txId = currentTransactionId;
    currentTransactionId = null;
    try {
        await fetch(`${API_URL}/transactions/${txId}/cancel`, { method: "PUT" });
    } catch (e) { console.error("Cancel error", e); }
}

function toggleQRBlur() {
    const qrContainer = document.querySelector(".qr-placeholder");
    const toggleBtn = document.getElementById("btn-toggle-qr");
    qrContainer.classList.toggle("blurred");
    toggleBtn.innerText = qrContainer.classList.contains("blurred") ? "Show QR Code" : "I've Scanned It";
}

// ==========================================
// MACHINE HEALTH & AUTO-LOCK SYSTEM
// ==========================================
async function checkMachineHealth() {
    const outOfServiceScreen = document.getElementById("out-of-service");
    
    try {
        const response = await fetch(`${API_URL}/inventory/`);
        
        if (response.ok) {
            const data = await response.json();
            
            // The Critical Thresholds
            // 1. Is the total cash less than our maximum allowed cashout (₱300)?
            // 2. Are we completely out of both ₱100 and ₱50 bills?
            const isCriticallyLow = data.total_value < 300 || (data.bill_100 < 1 && data.bill_50 < 1);
            
            if (isCriticallyLow) {
                outOfServiceScreen.style.display = "flex"; // Lock the machine
            } else {
                outOfServiceScreen.style.display = "none"; // Unlock the machine
            }
        } else {
            // If the server returns a 500 or 404 error, lock it down
            outOfServiceScreen.style.display = "flex";
        }
    } catch (error) {
        // If the FastAPI server is turned off completely, lock it down
        console.error("Heartbeat failed: Backend offline");
        outOfServiceScreen.style.display = "flex";
    }
}

// Run the check instantly when the kiosk boots up
checkMachineHealth();

// Then run it every 30 seconds to keep an eye on things
setInterval(checkMachineHealth, 30000);