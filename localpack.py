from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import re

def setup_driver():
    """Set up Chrome driver with optimal settings"""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to run headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    # Execute script to hide automation indicators
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def search_google(driver, query):
    """Perform Google search"""
    print(f"Searching for: {query}")
    
    # Navigate to Google
    driver.get('https://www.google.com')
    
    # Handle cookie consent if present
    try:
        consent_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'I agree')]"))
        )
        consent_button.click()
        time.sleep(1)
    except:
        pass
    
    # Find and use search box
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'q'))
    )
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    
    # Wait for search results to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'search'))
    )
    
    print("Search completed successfully")

def extract_local_pack_optimized(driver):
    """Optimized method based on your output findings"""
    local_businesses = []
    
    try:
        print("Using optimized extraction based on your output...")
        
        # Method 1: Use [data-cid] selector (most reliable based on your output)
        businesses = driver.find_elements(By.CSS_SELECTOR, '[data-cid]')
        print(f"Found {len(businesses)} businesses with [data-cid] selector")
        
        for i, business in enumerate(businesses):
            try:
                business_data = {}
                business_data['method'] = 'data-cid'
                business_data['index'] = i + 1
                
                # Get the container element
                business_data['element_class'] = business.get_attribute('class')
                business_data['data_cid'] = business.get_attribute('data-cid')
                
                # Extract business name (try multiple selectors)
                name_selectors = [
                    'span',
                    'div span',
                    '[role="link"]',
                    'h3',
                    '.fontHeadlineSmall'
                ]
                
                for selector in name_selectors:
                    try:
                        name_elements = business.find_elements(By.CSS_SELECTOR, selector)
                        for name_elem in name_elements:
                            text = name_elem.text.strip()
                            # Filter out ratings, addresses, etc.
                            if text and len(text) > 2 and not re.match(r'^[\d\.\(\)]+', text) and 'km' not in text.lower():
                                business_data['name'] = text
                                break
                        if 'name' in business_data:
                            break
                    except:
                        continue
                
                # Extract rating
                try:
                    rating_elements = business.find_elements(By.CSS_SELECTOR, '[role="img"]')
                    for rating_elem in rating_elements:
                        aria_label = rating_elem.get_attribute('aria-label')
                        if aria_label and 'star' in aria_label.lower():
                            business_data['rating'] = aria_label
                            break
                    
                    # Alternative: look for rating text
                    if 'rating' not in business_data:
                        rating_pattern = r'(\d+\.?\d*)\s*\([\d,]+\)'
                        full_text = business.text
                        rating_match = re.search(rating_pattern, full_text)
                        if rating_match:
                            business_data['rating'] = rating_match.group(0)
                except:
                    business_data['rating'] = 'No rating found'
                
                # Extract full text for debugging
                business_data['full_text'] = business.text[:200] + "..." if len(business.text) > 200 else business.text
                
                # Extract href if it's a link
                try:
                    href = business.get_attribute('href')
                    if href:
                        business_data['url'] = href
                except:
                    pass
                
                local_businesses.append(business_data)
                
            except Exception as e:
                print(f"Error extracting business {i+1}: {e}")
        
        # Method 2: Fallback to VkpGBb class
        if len(local_businesses) < 3:
            print("Trying VkpGBb selector as fallback...")
            vkpgbb_elements = driver.find_elements(By.CLASS_NAME, 'VkpGBb')
            
            for i, element in enumerate(vkpgbb_elements):
                try:
                    business_data = {}
                    business_data['method'] = 'VkpGBb'
                    business_data['index'] = i + 1
                    business_data['element_class'] = element.get_attribute('class')
                    business_data['full_text'] = element.text[:200] + "..." if len(element.text) > 200 else element.text
                    
                    # Look for business name in child elements
                    spans = element.find_elements(By.TAG_NAME, 'span')
                    for span in spans:
                        text = span.text.strip()
                        if text and len(text) > 3 and not re.match(r'^[\d\.\(\)]+', text):
                            business_data['name'] = text
                            break
                    
                    if business_data.get('full_text', '').strip():
                        local_businesses.append(business_data)
                        
                except Exception as e:
                    print(f"Error with VkpGBb element {i+1}: {e}")
        
    except Exception as e:
        print(f"Optimized extraction failed: {e}")
    
    return local_businesses

def parse_local_pack_from_main_container(driver):
    """Parse the local pack from the main bzXtMb container"""
    local_businesses = []
    
    try:
        # Get the main container (bzXtMb M8OgIe dRpWwb)
        main_container = driver.find_element(By.CSS_SELECTOR, '.bzXtMb.M8OgIe.dRpWwb')
        full_text = main_container.text
        
        print("Parsing text from main container...")
        print(f"Full text length: {len(full_text)} characters")
        
        # Split the text and look for business patterns
        lines = full_text.split('\n')
        current_business = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line looks like a business name (not rating, not address)
            if (len(line) > 3 and 
                not re.match(r'^\d+\.?\d*\s*\(', line) and  # Not rating like "4.7(859)"
                not re.match(r'^\$+\s*·', line) and        # Not price like "$$"
                not line.startswith('Plot #') and          # Not address
                not line.startswith('Sarwar Rd') and       # Not address
                not line.endswith('Chowk') and             # Not address ending
                'Search Results' not in line and
                'Choose area' not in line and
                'More places' not in line):
                
                # This might be a business name
                if current_business:
                    local_businesses.append(current_business)
                
                current_business = {
                    'name': line,
                    'method': 'text_parsing',
                    'raw_text': []
                }
            
            # Add to current business context
            if current_business:
                current_business['raw_text'].append(line)
                
                # Look for rating
                rating_match = re.search(r'(\d+\.?\d*)\s*\([\d,]+\)', line)
                if rating_match and 'rating' not in current_business:
                    current_business['rating'] = rating_match.group(0)
                
                # Look for price
                if '$' in line and 'price' not in current_business:
                    current_business['price'] = line
        
        # Add the last business
        if current_business:
            local_businesses.append(current_business)
        
        # Clean up the results
        cleaned_businesses = []
        for business in local_businesses:
            if (business.get('name') and 
                business['name'] not in ['Places', 'Map', 'Terms'] and
                len(business['name']) > 2):
                business['full_context'] = ' | '.join(business.get('raw_text', []))
                cleaned_businesses.append(business)
        
        return cleaned_businesses
        
    except Exception as e:
        print(f"Text parsing failed: {e}")
        return []

def print_results(businesses, method_name):
    """Print extracted business data"""
    if businesses:
        print(f"\n=== {method_name} Results ===")
        for i, business in enumerate(businesses, 1):
            print(f"\nBusiness {i}:")
            for key, value in business.items():
                if key != 'raw_text':  # Skip raw_text to keep output clean
                    print(f"  {key}: {value}")
    else:
        print(f"\n{method_name}: No local pack found")

def main():
    """Main function to run the optimized local pack scraper"""
    
    # Search queries to try
    queries = [
        "best pizza near me",
        "restaurants in lahore", 
        "coffee shops near me"
    ]
    
    # Choose a query
    query = queries[0]  # Use the same query that worked in your test
    
    # Set up driver
    driver = setup_driver()
    
    try:
        # Perform search
        search_google(driver, query)
        
        # Wait a bit for everything to load
        time.sleep(3)
        
        print("\n" + "="*60)
        print("EXTRACTING LOCAL PACK - OPTIMIZED BASED ON YOUR OUTPUT")
        print("="*60)
        
        # Method 1: Optimized extraction
        optimized_results = extract_local_pack_optimized(driver)
        print_results(optimized_results, "Optimized Method (data-cid & VkpGBb)")
        
        # Method 2: Text parsing from main container
        parsed_results = parse_local_pack_from_main_container(driver)
        print_results(parsed_results, "Text Parsing Method")
        
        # Summary
        print(f"\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Optimized method found: {len(optimized_results)} businesses")
        print(f"Text parsing found: {len(parsed_results)} businesses")
        
        if optimized_results:
            print("\nBusinesses found via optimized method:")
            for i, business in enumerate(optimized_results, 1):
                name = business.get('name', 'Unknown')
                rating = business.get('rating', 'No rating')
                print(f"  {i}. {name} - {rating}")
        
        if parsed_results:
            print("\nBusinesses found via text parsing:")
            for i, business in enumerate(parsed_results, 1):
                name = business.get('name', 'Unknown')
                rating = business.get('rating', 'No rating')
                print(f"  {i}. {name} - {rating}")
        
        # Keep browser open for manual inspection
        input("\nPress Enter to close the browser...")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()