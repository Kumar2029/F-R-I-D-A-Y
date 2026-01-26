
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

# Load HTML content
current_dir = os.getcwd()
Link = f"{current_dir}/Data/Voice.html"
link_url = "file:///" + Link.replace("\\", "/")

print(f"Loading URL: {link_url}")

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
# chrome_options.add_argument("--headless=new") # DISABLED for debugging
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36")

# Enable logging
d = webdriver.DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = { 'browser':'ALL' }
chrome_options.set_capability('goog:loggingPrefs', { 'browser':'ALL' })

try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get(link_url)
    print("Page loaded.")

    start_button = driver.find_element(By.ID, "start")
    start_button.click()
    print("Clicked start button. Speak now...")

    # Poll for output
    for i in range(20): # Try for 20 seconds
        try:
            output_element = driver.find_element(By.ID, "output")
            text = output_element.text
            if text:
                print(f"Captured Text: {text}")
                break
        except Exception as e:
            print(f"Error reading output: {e}")
        
        # Check console logs
        logs = driver.get_log('browser')
        for log in logs:
            print(f"Browser Log: {log}")
            
        time.sleep(1)
    else:
        print("Timeout: No speech detected in 20 seconds.")

except Exception as e:
    print(f"Fatal Error: {e}")
finally:
    if 'driver' in locals():
        # driver.quit() 
        pass 
