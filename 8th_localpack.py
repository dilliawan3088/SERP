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

# Locate the search box (By name is very common for input fields)
search_box = driver.find_element(By.NAME, "q")

# Type the user's input into the search box
search_box.send_keys(search_query)

# Press "Enter" to submit the search
search_box.send_keys(Keys.RETURN)

# Wait for the results to load (wait until the first result is visible)
WebDriverWait(driver, 60).until(
    EC.visibility_of_element_located((By.ID, "search"))
)

# Fetch the top 3 businesses in the local pack (using CSS selectors)
businesses = []

# 1st business using data-cid
first_business = driver.find_element(By.CSS_SELECTOR, '[data-cid]')
first_business_data = {}
first_business_data['name'] = first_business.find_element(By.CSS_SELECTOR, '.OSrXXb').text.strip()
first_business_data['rating'] = first_business.find_element(By.CSS_SELECTOR, '.yi40Hd').text.strip()
first_business_data['review_count'] = first_business.find_element(By.CSS_SELECTOR, '.RDApEe').text.strip()
first_business_data['address'] = first_business.find_element(By.CSS_SELECTOR, '.rllt__details span').text.strip()
first_business_data['description'] = first_business.find_element(By.CSS_SELECTOR, '.uDyWh').text.strip()

businesses.append(first_business_data)

# 2nd business using class VkpGBb
second_business = driver.find_element(By.CLASS_NAME, 'VkpGBb')
second_business_data = {}

second_business_data['name'] = second_business.find_element(By.CSS_SELECTOR, '.OSrXXb').text.strip()
second_business_data['rating'] = second_business.find_element(By.CSS_SELECTOR, '.yi40Hd').text.strip()
second_business_data['review_count'] = second_business.find_element(By.CSS_SELECTOR, '.RDApEe').text.strip()
second_business_data['address'] = second_business.find_element(By.CSS_SELECTOR, '.rllt__details span').text.strip()
second_business_data['description'] = second_business.find_element(By.CSS_SELECTOR, '.uDyWh').text.strip()

businesses.append(second_business_data)

# 3rd business using data-cid again (adjust this part if needed)
third_business = driver.find_elements(By.CSS_SELECTOR, '[data-cid]')[2]
third_business_data = {}
third_business_data['name'] = third_business.find_element(By.CSS_SELECTOR, '.OSrXXb').text.strip()
third_business_data['rating'] = third_business.find_element(By.CSS_SELECTOR, '.yi40Hd').text.strip()
third_business_data['review_count'] = third_business.find_element(By.CSS_SELECTOR, '.RDApEe').text.strip()
third_business_data['address'] = third_business.find_element(By.CSS_SELECTOR, '.rllt__details span').text.strip()
third_business_data['description'] = third_business.find_element(By.CSS_SELECTOR, '.uDyWh').text.strip()

businesses.append(third_business_data)

# Display the extracted business data
print("\nTop 3 Businesses:")
for idx, business in enumerate(businesses, 1):
    print(f"\nBusiness {idx}:")
    for key, value in business.items():
        print(f"  {key}: {value}")

# Close the browser after all actions
driver.quit()
