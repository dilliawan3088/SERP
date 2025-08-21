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
import json

def setup_driver():
    """Set up Chrome driver with optimal settings"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def search_google(driver, query):
    """Perform Google search"""
    print(f"Searching for: {query}")
    
    driver.get('https://www.google.com')
    
    try:
        consent_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'I agree')]"))
        )
        consent_button.click()
        time.sleep(1)
    except:
        pass
    
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'q'))
    )
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'search'))
    )
    
    print("Search completed successfully")

def extract_businesses_from_data_cid(driver):
    """Extract individual businesses using [data-cid] elements"""
    businesses = []
    
    try:
        # Find all elements with data-cid attribute
        cid_elements = driver.find_elements(By.CSS_SELECTOR, '[data-cid]')
        print(f"Found {len(cid_elements)} elements with [data-cid]")
        
        for i, element in enumerate(cid_elements):
            try:
                business = {}
                business['method'] = 'data-cid'
                business['index'] = i + 1
                business['data_cid'] = element.get_attribute('data-cid')
                business['element_class'] = element.get_attribute('class')
                business['tag_name'] = element.tag_name
                
                # Get the clickable area text (usually the business name)
                business['clickable_text'] = element.text.strip()
                
                # Get href if it's a link
                href = element.get_attribute('href')
                if href:
                    business['url'] = href
                
                # Try to find parent container for more context
                try:
                    parent = element.find_element(By.XPATH, './..')
                    business['parent_class'] = parent.get_attribute('class')
                    business['parent_text'] = parent.text[:100] + "..." if len(parent.text) > 100 else parent.text
                except:
                    pass
                
                # Look for nearby rating elements
                try:
                    # Check siblings and nearby elements for ratings
                    parent = element.find_element(By.XPATH, './..')
                    rating_elements = parent.find_elements(By.CSS_SELECTOR, '[role="img"], span')
                    for rating_elem in rating_elements:
                        text = rating_elem.text.strip()
                        aria_label = rating_elem.get_attribute('aria-label')
                        
                        # Check for star ratings in aria-label
                        if aria_label and 'star' in aria_label.lower():
                            business['rating_aria'] = aria_label
                        
                        # Check for rating patterns in text
                        if re.match(r'\d+\.?\d*\s*\([\d,]+\)', text):
                            business['rating_text'] = text
                except:
                    pass
                
                businesses.append(business)
                
            except Exception as e:
                print(f"Error processing data-cid element {i+1}: {e}")
    
    except Exception as e:
        print(f"Error in extract_businesses_from_data_cid: {e}")
    
    return businesses

def extract_businesses_detailed_search(driver):
    """Detailed search for business information using multiple strategies"""
    businesses = []
    
    try:
        # Strategy 1: Look for business containers by common patterns
        container_selectors = [
            '[data-cid]',
            '.VkpGBb',
            '[jsaction*="mouseover"]',
            '[data-ved][role="link"]',
            '.rllt__link'
        ]
        
        all_containers = []
        for selector in container_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Found {len(elements)} elements with selector: {selector}")
                for elem in elements:
                    if elem not in all_containers:
                        all_containers.append((elem, selector))
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
        
        print(f"Total unique containers found: {len(all_containers)}")
        
        # Process each container
        for i, (container, selector_used) in enumerate(all_containers):
            try:
                business = {}
                business['method'] = f'detailed_search_{selector_used}'
                business['index'] = i + 1
                business['selector_used'] = selector_used
                business['element_class'] = container.get_attribute('class')
                business['tag_name'] = container.tag_name
                
                # Get all attributes
                attributes = {}
                for attr in ['data-cid', 'data-ved', 'role', 'href', 'aria-label']:
                    value = container.get_attribute(attr)
                    if value:
                        attributes[attr] = value
                business['attributes'] = attributes
                
                # Get text content
                text = container.text.strip()
                if text:
                    business['text_content'] = text[:150] + "..." if len(text) > 150 else text
                
                # Look for business name patterns
                if text:
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        # Business name is usually the first substantial line that's not a rating
                        if (len(line) > 3 and 
                            not re.match(r'^\d+\.?\d*\s*\(', line) and 
                            not line.startswith('$') and
                            'star' not in line.lower()):
                            business['potential_name'] = line
                            break
                
                # Look for rating in text
                rating_match = re.search(r'(\d+\.?\d*)\s*\([\d,]+\)', text)
                if rating_match:
                    business['rating_found'] = rating_match.group(0)
                
                businesses.append(business)
                
            except Exception as e:
                print(f"Error processing container {i+1}: {e}")
    
    except Exception as e:
        print(f"Error in extract_businesses_detailed_search: {e}")
    
    return businesses

def extract_from_specific_structure(driver):
    """Extract based on the specific structure seen in your output"""
    businesses = []
    
    try:
        # Based on your output, look for the specific class structure
        # Class names from your debug: 'vwVdIc wzN8Ac rllt__link a-no-hover-decoration'
        
        business_link_selectors = [
            '.vwVdIc.wzN8Ac.rllt__link.a-no-hover-decoration',
            '.uQ4NLd.b9tNq.wzN8Ac.rllt__link.a-no-hover-decoration',
            '.rllt__link[data-cid]',
            'a[data-cid]'
        ]
        
        for selector in business_link_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Found {len(elements)} elements with specific selector: {selector}")
                
                for i, element in enumerate(elements):
                    business = {}
                    business['method'] = f'specific_structure_{selector}'
                    business['index'] = i + 1
                    business['element_class'] = element.get_attribute('class')
                    business['data_cid'] = element.get_attribute('data-cid')
                    
                    # Get the href (business link)
                    href = element.get_attribute('href')
                    if href:
                        business['business_url'] = href
                    
                    # Get aria-label which often contains business name
                    aria_label = element.get_attribute('aria-label')
                    if aria_label:
                        business['aria_label'] = aria_label
                        # Aria-label often contains: "Business Name · Rating · Type · Address"
                        if '·' in aria_label:
                            parts = aria_label.split('·')
                            business['parsed_name'] = parts[0].strip()
                            if len(parts) > 1:
                                business['parsed_rating'] = parts[1].strip()
                            if len(parts) > 2:
                                business['parsed_type'] = parts[2].strip()
                    
                    # Get text content
                    text = element.text.strip()
                    if text:
                        business['text_content'] = text
                    
                    # Try to find child elements with business details
                    try:
                        spans = element.find_elements(By.TAG_NAME, 'span')
                        div_elements = element.find_elements(By.TAG_NAME, 'div')
                        
                        business['child_spans'] = len(spans)
                        business['child_divs'] = len(div_elements)
                        
                        # Get text from first few spans (often contain name, rating, etc.)
                        span_texts = []
                        for span in spans[:5]:
                            span_text = span.text.strip()
                            if span_text:
                                span_texts.append(span_text)
                        business['span_texts'] = span_texts
                        
                    except Exception as e:
                        print(f"Error getting child elements: {e}")
                    
                    businesses.append(business)
                    
            except Exception as e:
                print(f"Error with specific selector {selector}: {e}")
    
    except Exception as e:
        print(f"Error in extract_from_specific_structure: {e}")
    
    return businesses

def enhanced_text_parsing(driver):
    """Enhanced text parsing from the main container"""
    businesses = []
    
    try:
        # Get the main local pack container
        main_container = driver.find_element(By.CSS_SELECTOR, '.bzXtMb.M8OgIe.dRpWwb')
        full_text = main_container.text
        
        print(f"Parsing enhanced text (length: {len(full_text)})")
        
        # Split into sections based on your output pattern
        # From your output: "Caprinos Pizza Gulberg", "Broadway Pizza - Shadman", "M Pizzeria"
        
        # Business pattern recognition
        business_patterns = [
            r'([A-Za-z\s\-&]+(?:Pizza|Restaurant|Cafe|Kitchen|Grill|Bar|Bistro|Eatery)[A-Za-z\s\-]*)',
            r'([A-Z][a-z]+ [A-Za-z\s\-]+ (?:Gulberg|Shadman|Road|Street|Boulevard))',
            r'^([A-Z][A-Za-z\s\-&]{3,}?)(?:\s+[\d\.]+\([\d,]+\)|\s+\$|\s+Rs|\s+·)',
        ]
        
        lines = full_text.split('\n')
        current_business = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a business name
            is_business_name = False
            
            # Pattern 1: Contains restaurant/food keywords
            if any(keyword in line.lower() for keyword in ['pizza', 'restaurant', 'cafe', 'kitchen', 'grill']):
                # Make sure it's not just a description
                if not re.match(r'^\d+\.?\d*\s*\(', line) and len(line) > 5:
                    is_business_name = True
            
            # Pattern 2: Starts with capital letter and has reasonable length
            elif (re.match(r'^[A-Z]', line) and 
                  len(line) > 3 and len(line) < 50 and
                  not re.match(r'^\d+\.?\d*\s*\(', line) and
                  line not in ['Places', 'Map', 'Terms', 'Choose area', 'Search Results', 'More places'] and
                  not line.startswith('Plot #') and
                  not line.endswith('Chowk')):
                is_business_name = True
            
            if is_business_name:
                # Save previous business
                if current_business:
                    businesses.append(current_business)
                
                # Start new business
                current_business = {
                    'name': line,
                    'method': 'enhanced_text_parsing',
                    'details': []
                }
            elif current_business:
                # Add details to current business
                current_business['details'].append(line)
                
                # Extract specific information
                if re.match(r'\d+\.?\d*\s*\([\d,]+\)', line):
                    current_business['rating'] = line
                elif '$' in line or 'Rs' in line:
                    current_business['price'] = line
                elif any(addr_word in line.lower() for addr_word in ['road', 'street', 'boulevard', 'plot', 'main']):
                    current_business['address'] = line
                elif line.startswith('"') and line.endswith('"'):
                    current_business['review_snippet'] = line
        
        # Add the last business
        if current_business:
            businesses.append(current_business)
        
        # Clean and format results
        cleaned_businesses = []
        for i, business in enumerate(businesses):
            if business.get('name') and len(business['name']) > 2:
                business['index'] = i + 1
                business['full_details'] = ' | '.join(business.get('details', []))
                cleaned_businesses.append(business)
        
        return cleaned_businesses
        
    except Exception as e:
        print(f"Enhanced text parsing failed: {e}")
        return []

def print_businesses(businesses, method_name):
    """Print business information in a readable format"""
    if not businesses:
        print(f"\n{method_name}: No businesses found")
        return
    
    print(f"\n{'='*50}")
    print(f"{method_name.upper()}")
    print(f"Found {len(businesses)} businesses")
    print(f"{'='*50}")
    
    for business in businesses:
        print(f"\n--- Business {business.get('index', '?')} ---")
        
        # Print key information first
        for key in ['name', 'parsed_name', 'potential_name']:
            if business.get(key):
                print(f"NAME: {business[key]}")
                break
        
        for key in ['rating', 'rating_found', 'parsed_rating']:
            if business.get(key):
                print(f"RATING: {business[key]}")
                break
        
        if business.get('business_url'):
            print(f"URL: {business['business_url']}")
        
        if business.get('address'):
            print(f"ADDRESS: {business['address']}")
        
        if business.get('price'):
            print(f"PRICE: {business['price']}")
        
        # Print technical details
        print(f"Method: {business.get('method', 'unknown')}")
        print(f"Element Class: {business.get('element_class', 'N/A')}")
        
        if business.get('data_cid'):
            print(f"Data CID: {business['data_cid']}")
        
        # Print additional context
        if business.get('aria_label'):
            print(f"Aria Label: {business['aria_label']}")
        
        if business.get('text_content'):
            print(f"Text Content: {business['text_content']}")
        
        if business.get('full_details'):
            print(f"Full Details: {business['full_details']}")

def main():
    """Main execution function"""
    query = "best pizza near me"  # Use the same query that worked
    
    driver = setup_driver()
    
    try:
        search_google(driver, query)
        time.sleep(3)
        
        print("\n" + "="*70)
        print("COMPREHENSIVE LOCAL PACK EXTRACTION")
        print("="*70)
        
        # Method 1: Data-CID extraction
        print("\n1. Extracting via [data-cid] elements...")
        cid_businesses = extract_businesses_from_data_cid(driver)
        print_businesses(cid_businesses, "Data-CID Method")
        
        # Method 2: Detailed search
        print("\n2. Performing detailed search...")
        detailed_businesses = extract_businesses_detailed_search(driver)
        print_businesses(detailed_businesses, "Detailed Search Method")
        
        # Method 3: Specific structure
        print("\n3. Using specific structure extraction...")
        specific_businesses = extract_from_specific_structure(driver)
        print_businesses(specific_businesses, "Specific Structure Method")
        
        # Method 4: Enhanced text parsing
        print("\n4. Enhanced text parsing...")
        parsed_businesses = enhanced_text_parsing(driver)
        print_businesses(parsed_businesses, "Enhanced Text Parsing")
        
        # Summary
        print(f"\n{'='*70}")
        print("EXTRACTION SUMMARY")
        print(f"{'='*70}")
        print(f"Data-CID method: {len(cid_businesses)} businesses")
        print(f"Detailed search: {len(detailed_businesses)} businesses")
        print(f"Specific structure: {len(specific_businesses)} businesses")
        print(f"Text parsing: {len(parsed_businesses)} businesses")
        
        # Show the best results
        all_methods = [
            (cid_businesses, "Data-CID"),
            (detailed_businesses, "Detailed Search"),
            (specific_businesses, "Specific Structure"),
            (parsed_businesses, "Text Parsing")
        ]
        
        best_method = max(all_methods, key=lambda x: len([b for b in x[0] if b.get('name') or b.get('parsed_name') or b.get('potential_name')]))
        
        print(f"\nBest performing method: {best_method[1]} with {len(best_method[0])} businesses")
        
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()