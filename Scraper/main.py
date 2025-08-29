import json
from searchResults import perform_google_search
from scrap import scrape_landing_page

def main():
    # Get search query from user
    search_query = input("Enter your search query: ")

    # Perform Google search and get results
    search_data = perform_google_search(search_query)
    
    # Initialize combined results
    combined_results = {
        "search_query": search_query,
        "search_results": search_data,
        "scraped_pages": {}
    }

    # Scrape each URL from the search results
    for result in search_data.get("top_results", []):
        url = result.get("url")
        if url:
            print(f"Scraping {url}...")
            try:
                scraped_content = scrape_landing_page(url)
                combined_results["scraped_pages"][url] = scraped_content.get(url, "")
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
                combined_results["scraped_pages"][url] = {"error": str(e)}

    # Save combined results to JSON
    output_file = "combined_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(combined_results, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved combined results to {output_file}")

if __name__ == "__main__":
    main()