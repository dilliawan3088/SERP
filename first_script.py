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

# Wait for cookies popup and click 'I agree'
try:
    agree_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'I agree') or contains(text(), 'Accept all')]"))
    )
    agree_button.click()
except:
    pass  # No cookie banner appeared

# Locate the search box and submit the query
search_box = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "q"))
)
search_box.send_keys(search_query)
search_box.send_keys(Keys.RETURN)

# Extended wait to handle potential CAPTCHA
print("Waiting for results to load... (up to 60 seconds)")
try:
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "search"))
    )
except:
    print("It seems like Google is blocking the request (CAPTCHA). Please solve it manually.")

# Now fetch proper result blocks
results = driver.find_elements(By.CSS_SELECTOR, "div.tF2Cxc")

# Display the results
print("\nTop Search Results:\n")
for idx, result in enumerate(results[:10], 1):
    try:
        title = result.find_element(By.TAG_NAME, "h3").text
        link = result.find_element(By.TAG_NAME, "a").get_attribute("href")
        print(f"{idx}. Title: {title}\n   URL: {link}\n")
    except:
        continue  # skip result if any element is missing

# Optionally, add a small sleep to avoid hammering Google with repeated requests
time.sleep(2)

# Close the browser
driver.quit()
