let currentTransaction = {
  wallet: null,
  amount: 0,
  phone: "",
  type: "cashout",
  fee: 0,
  total: 0,
};

let currentInputId = "input-amount";
let idleTimer;

// Initialize when page loads
document.addEventListener("DOMContentLoaded", () => {
  const idleSection = document.getElementById("sec-idle");
  idleSection.addEventListener("click", () => {
    showSection("sec-home");
  });

  updateDateTime();
  setInterval(updateDateTime, 1000);
  resetIdle();
});

function resetTransaction() {
  currentTransaction = {
    wallet: null,
    amount: null,
    status: "pending",
    type: "cashout",
    fee: 0,
  };
}

// Update the visual progress bar based on the current screen
function updateProgressBar(sectionId) {
  const progressBar = document.getElementById("progress-bar");

  // Only show the progress bar on transaction screens
  if (sectionId === "sec-idle" || sectionId === "sec-home") {
    progressBar.style.display = "none";
    return;
  } else {
    progressBar.style.display = "flex";
  }

  // Map the HTML section IDs to their step numbers
  const stepsMapping = {
    "sec-amount": 1,
    "sec-qr": 2,
    "sec-processing": 3,
    "sec-receipt": 4,
  };

  const currentStep = stepsMapping[sectionId] || 1;

  for (let i = 1; i <= 4; i++) {
    const stepEl = document.getElementById(`step-${i}`);
    const lineEl = document.getElementById(`line-${i - 1}`); // The line trailing behind the step

    if (i < currentStep) {
      // Completed steps (turn blue, checkmark)
      stepEl.className = "step completed";
      stepEl.querySelector(".circle").innerHTML = "<i class='bx bx-check'></i>";
      if (lineEl) lineEl.className = "line active";
    } else if (i === currentStep) {
      // Current active step (highlighted)
      stepEl.className = "step active";
      stepEl.querySelector(".circle").innerHTML = i;
      if (lineEl) lineEl.className = "line active";
    } else {
      // Future steps (grey)
      stepEl.className = "step";
      stepEl.querySelector(".circle").innerHTML = i;
      if (lineEl) lineEl.className = "line";
    }
  }
}

function showSection(sectionId) {
  if (sectionId === "sec-home") {
    resetTransaction();
  }

  document.querySelectorAll(".kiosk-section").forEach((sec) => {
    sec.classList.remove("active");
  });

  const target = document.getElementById(sectionId);
  if (target) {
    target.classList.add("active");
  }

  // Tell the progress bar to update whenever the screen changes!
  updateProgressBar(sectionId);
  resetIdle();
}

// Numpad Functions
function appendNum(num) {
  const input = document.getElementById(currentInputId);
  if (input) input.value += num;
}

function setExactAmount(amount) {
  const input = document.getElementById(currentInputId);
  if (input) {
    // Instantly replaces the entire value
    input.value = amount;
  }
}

function clearNum() {
  const input = document.getElementById(currentInputId);
  if (input) input.value = "";
}

function deleteNum() {
  const input = document.getElementById(currentInputId);
  if (input) input.value = input.value.slice(0, -1);
}

// Global Nav Button Listener
document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-target]");
  if (btn) {
    const sectionId = btn.getAttribute("data-target");
    if (sectionId) showSection(sectionId);
  }
});

// Idle Handling
function resetIdle() {
  clearTimeout(idleTimer);
  idleTimer = setTimeout(() => {
    if (typeof cancelCurrentTransaction === "function") {
      cancelCurrentTransaction();
    }
    showSection("sec-idle");
  }, 120000); // 120 seconds
}

document.onclick = resetIdle;

// Date & Time
function updateDateTime() {
  const display = document.getElementById("datetime-display");
  const now = new Date();
  const dateStr = now.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "2-digit",
    year: "numeric",
  });
  const timeStr = now.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
  display.innerHTML = `${dateStr} <br> ${timeStr}`;
}

function toggleQRBlur() {
  const qrContainer = document.querySelector(".qr-placeholder");
  const toggleBtn = document.getElementById("btn-toggle-qr");

  // This adds the blur if it's missing, or removes it if it's there
  qrContainer.classList.toggle("blurred");

  // Swap the text and color so the user knows they can reverse it
  if (qrContainer.classList.contains("blurred")) {
    toggleBtn.innerText = "Show QR Code";
    toggleBtn.style.background = "#888"; // Make it grey so it looks less prominent
  } else {
    toggleBtn.innerText = "I've Scanned It";
    toggleBtn.style.background = "var(--primary)"; // Reset to your main color
  }
}

// Shows the custom alert box
function showCustomAlert(message, title = "Notice") {
  document.getElementById("modal-title").innerText = title;
  document.getElementById("modal-message").innerText = message;
  document.getElementById("custom-alert").style.display = "flex";
}

// Hides it when they click Okay
function closeCustomAlert() {
  document.getElementById("custom-alert").style.display = "none";
}
