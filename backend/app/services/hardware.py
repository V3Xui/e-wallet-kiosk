import serial
import time
import threading

# Configuration Parameters
PORT = "COM6"
BAUD_RATE = 9600

_serial_connection = None
_lock = threading.Lock()

def get_serial_port():
    """Initializes and balances a single shared serial connection."""
    global _serial_connection
    with _lock:
        if _serial_connection is None:
            try:
                _serial_connection = serial.Serial(PORT, BAUD_RATE, timeout=1)
                time.sleep(2) # Allow Arduino bootloader initialization time
                print(f"🔌 Serial Connection established successfully on {PORT}")
            except Exception as e:
                print(f"⚠️ Hardware Warning: Could not open port {PORT}. Running in mock mode. Error: {e}")
                _serial_connection = False
        return _serial_connection

def send_dispense_command(h100: int, f50: int, t20: int):
    """Formats and transmits the smart-matrix instructions to the Arduino."""
    ser = get_serial_port()
    command_string = f"DISPENSE:{h100},{f50},{t20}\n"
    
    if ser:
        try:
            ser.write(command_string.encode('utf-8'))
            print(f"💾 Serial Stream Sent: {command_string.strip()}")
            
            # Read immediate confirmation back from Arduino
            response = ser.readline().decode('utf-8').strip()
            print(f"📥 Arduino Response: {response}")
            return True
        except Exception as e:
            print(f"❌ Serial Write Error: {e}")
            return False
    else:
        print(f"🤖 [Mock Mode] Hardware disconnected. Command would be: {command_string.strip()}")
        return True