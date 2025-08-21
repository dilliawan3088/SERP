from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

# Fetch the top 10 search results
results = driver.find_elements(By.CSS_SELECTOR, 'h3')  # Titles of the results
links = driver.find_elements(By.CSS_SELECTOR, 'a')  # URLs of the results

# Print the top 10 search results
top_results = []
for i in range(min(10, len(results))):
    title = results[i].text
    url = links[i].get_attribute('href')
    if url:  # Check if the URL is valid
        top_results.append((title, url))

# Display the top 10 search results
print("Top 10 Search Results:")
for idx, (title, url) in enumerate(top_results, 1):
    print(f"{idx}. Title: {title}\n   URL: {url}\n")

# Fetch the "People also ask" questions
people_also_ask = driver.find_elements(By.CSS_SELECTOR, '.related-question-pair')  # People also ask section
questions = [question.text for question in people_also_ask]

# Display the questions
print("\nPeople Also Ask:")
for idx, question in enumerate(questions, 1):
    print(f"{idx}. {question}")

# Fetch the Featured Snippet using the updated XPath (if it exists)
try:
    # Using the class "VNzqVe" to locate the featured snippet (adjusted for generalization)
    featured_snippet = driver.find_element(By.XPATH, "//div[contains(@class, 'VNzqVe')]")
    print("\nFeatured Snippet:")
    print(featured_snippet.text)
except Exception as e:
    print("\nNo featured snippet found.")

# Count the number of top ads (ads above the organic results)
top_ads = driver.find_elements(By.CSS_SELECTOR, "div[data-hveid='CAQQAQ']")  # Update this CSS selector as needed
print("\nNumber of Top Ads:", len(top_ads))

# Count the number of bottom ads (ads below the organic results)
bottom_ads = driver.find_elements(By.CSS_SELECTOR, "div[data-hveid='CAQQAQ']")  # Update this CSS selector as needed
print("Number of Bottom Ads:", len(bottom_ads))


# Close the browser
driver.quit()
