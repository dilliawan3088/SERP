from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
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

# Fetch the Featured Snippet using the updated XPath (if it exists)
try:
    # Using the class "VNzqVe" to locate the featured snippet (adjusted for generalization)
    featured_snippet = driver.find_element(By.XPATH, "//div[contains(@class, 'VNzqVe')]")
    print("\nFeatured Snippet:")
    print(featured_snippet.text)
except Exception as e:
    print("\nNo featured snippet found.")

# Fetch the "People also ask" questions
people_also_ask = driver.find_elements(By.CSS_SELECTOR, '.related-question-pair')  # People also ask section
questions = [question.text for question in people_also_ask]

# Display the questions
print("\nPeople Also Ask:")
for idx, question in enumerate(questions, 1):
    print(f"{idx}. {question}")

# Fetch the Video Links (typically YouTube or embedded video links)
video_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="youtube.com"]')  # Look for YouTube links
video_urls = [video.get_attribute('href') for video in video_links]

# Display the video links
if video_urls:
    print("\nVideo Links:")
    for idx, video_url in enumerate(video_urls, 1):
        print(f"{idx}. {video_url}")
else:
    print("\nNo video links found.")

# Count the number of top ads (ads above the organic results)
top_ads = driver.find_elements(By.CSS_SELECTOR, "div[data-hveid='CAQQAQ']")  # Update this CSS selector as needed
print("\nNumber of Top Ads:", len(top_ads))

# Count the number of bottom ads (ads below the organic results)
bottom_ads = driver.find_elements(By.CSS_SELECTOR, "div[data-hveid='CAQQAQ']")  # Update this CSS selector as needed
print("Number of Bottom Ads:", len(bottom_ads))

# Wait for the AI Overview Section (WaaZC class) to load after the results and ads are fetched
try:
    # Ensure we allow some time for the AI overview to load
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "WaaZC"))
    )
    ai_overview = driver.find_element(By.CLASS_NAME, "WaaZC")
    print("\nAI Overview Section:")
    print(ai_overview.text)
except Exception as e:
    print("\nNo AI Overview Section found.")

# Fetch Image Links (Images on the page)
image_links = driver.find_elements(By.CSS_SELECTOR, 'img')  # Find all image tags
image_urls = [img.get_attribute('src') for img in image_links if img.get_attribute('src')]

# Display Image Links
if image_urls:
    print("\nImage Links:")
    for idx, img_url in enumerate(image_urls, 1):
        print(f"{idx}. {img_url}")
else:
    print("\nNo image links found.")

# Fetch the Site Links (URLs from the SERP that lead to other pages in the same domain)
site_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="https://"]')  # Filter links starting with 'https://'
site_urls = [link.get_attribute('href') for link in site_links]

# Display the site links
if site_urls:
    print("\nSite Links:")
    for idx, site_url in enumerate(site_urls, 1):
        print(f"{idx}. {site_url}")
else:
    print("\nNo site links found.")

# Fetch the top 3 businesses in the local pack (using CSS selectors)
businesses = []

# 1st business using data-cid
try:
    first_business = driver.find_element(By.CSS_SELECTOR, '[data-cid]')
    first_business_data = {}
    first_business_data['name'] = first_business.find_element(By.CSS_SELECTOR, '.OSrXXb').text.strip()
    first_business_data['rating'] = first_business.find_element(By.CSS_SELECTOR, '.yi40Hd').text.strip()
    first_business_data['review_count'] = first_business.find_element(By.CSS_SELECTOR, '.RDApEe').text.strip()
    first_business_data['address'] = first_business.find_element(By.CSS_SELECTOR, '.rllt__details span').text.strip()
    first_business_data['description'] = first_business.find_element(By.CSS_SELECTOR, '.uDyWh').text.strip()
    businesses.append(first_business_data)
except NoSuchElementException:
    print("No local pack found for 1st business.")

# 2nd business using class VkpGBb
try:
    second_business = driver.find_element(By.CLASS_NAME, 'VkpGBb')
    second_business_data = {}
    second_business_data['name'] = second_business.find_element(By.CSS_SELECTOR, '.OSrXXb').text.strip()
    second_business_data['rating'] = second_business.find_element(By.CSS_SELECTOR, '.yi40Hd').text.strip()
    second_business_data['review_count'] = second_business.find_element(By.CSS_SELECTOR, '.RDApEe').text.strip()
    second_business_data['address'] = second_business.find_element(By.CSS_SELECTOR, '.rllt__details span').text.strip()
    second_business_data['description'] = second_business.find_element(By.CSS_SELECTOR, '.uDyWh').text.strip()
    businesses.append(second_business_data)
except NoSuchElementException:
    print("No local pack found for 2nd business.")

# 3rd business using data-cid again
try:
    third_business = driver.find_elements(By.CSS_SELECTOR, '[data-cid]')[2]
    third_business_data = {}
    third_business_data['name'] = third_business.find_element(By.CSS_SELECTOR, '.OSrXXb').text.strip()
    third_business_data['rating'] = third_business.find_element(By.CSS_SELECTOR, '.yi40Hd').text.strip()
    third_business_data['review_count'] = third_business.find_element(By.CSS_SELECTOR, '.RDApEe').text.strip()
    third_business_data['address'] = third_business.find_element(By.CSS_SELECTOR, '.rllt__details span').text.strip()
    third_business_data['description'] = third_business.find_element(By.CSS_SELECTOR, '.uDyWh').text.strip()
    businesses.append(third_business_data)
except NoSuchElementException:
    print("No local pack found for 3rd business.")

# Display the extracted business data
if businesses:
    print("\nTop 3 Businesses:")
    for idx, business in enumerate(businesses, 1):
        print(f"\nBusiness {idx}:")
        for key, value in business.items():
            print(f"  {key}: {value}")
else:
    print("No local pack found.")

# Close the browser after all actions
driver.quit()
