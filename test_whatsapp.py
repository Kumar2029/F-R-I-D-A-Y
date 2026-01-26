from Backend.Automation import OpenApp
import time

def test_whatsapp():
    print("Attempting to open WhatsApp...")
    OpenApp("whatsapp")
    print("Wait 5 seconds...")
    time.sleep(5)
    print("Test complete. Did it open?")

if __name__ == "__main__":
    test_whatsapp()
