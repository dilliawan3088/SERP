from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Ask for user input
search_query = input("Enter your search query: ")

# Setup the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open Google
driver.get("https://www.google.com")

# Locate the search box
search_box = driver.find_element(By.NAME, "q")

# Type the user's input into the search box
search_box.send_keys(search_query)

# Press "Enter" to submit the search
search_box.send_keys(Keys.RETURN)

# Wait for the results to load (wait until the first result is visible)
WebDriverWait(driver, 60).until(
    EC.visibility_of_element_located((By.ID, "search"))
)

# Wait for the AI Overview Section (WaaZC class)
try:
    # Wait for the AI Overview section to load
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "WaaZC"))
    )
    ai_overview = driver.find_element(By.CLASS_NAME, "WaaZC")
    print("\nAI Overview Section:")
    print(ai_overview.text)
except Exception as e:
    print("\nNo AI Overview Section found.")

# Close the browser
driver.quit()
