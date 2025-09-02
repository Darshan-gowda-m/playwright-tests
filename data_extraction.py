# MIT License
# Copyright (c) 2025 Dharshan Gowda M
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, TimeoutError, expect

class DataExtractor:
    def __init__(self, url, session_file="session.json"):
        self.url = url
        self.session_file = Path(session_file)
        self.data = []
        self.max_products = None

    def run(self, username=None, password=None, max_products=2505):
        """
        Main method to run the data extraction process
        """
        self.max_products = max_products
        
        # Load credentials from config file if not provided
        if not username or not password:
            config = self._load_config()
            username = config.get("username", username)
            password = config.get("password", password)
        
        with sync_playwright() as playwright:
            # Launch browser in non-headless mode for debugging
            browser = playwright.chromium.launch(headless=False)
            context = None

            # Try to load existing session if available
            if self.session_file.exists():
                print("Loading existing session...")
                context = browser.new_context(storage_state=str(self.session_file))
            else:
                print("Creating new session...")
                context = browser.new_context()

            page = context.new_page()
            # Set a reasonable default timeout
            page.set_default_timeout(30000)

            try:
                print(f"Navigating to {self.url}...")
                page.goto(self.url)
                # Wait for network to be idle
                page.wait_for_load_state("networkidle")
                
                # Check if login is required
                if self._is_login_required(page):
                    print("Login required detected...")
                    if not username or not password:
                        raise ValueError("Login required but credentials not provided")
                    self._login(page, username, password)
                    # Save session state for future use
                    context.storage_state(path=str(self.session_file))
                    print("Login successful, session saved.")

                # Navigate to challenge page
                print("Navigating to challenge page...")
                page.goto(f"{self.url.rstrip('/')}/challenge")
                page.wait_for_load_state("networkidle")
                time.sleep(2)
                
                # Navigate to products section
                print("Navigating to products...")
                self._navigate_to_products(page)
                
                # Extract product data
                print("Extracting product data...")
                self._extract_product_data(page)
                
                # Export data to JSON file
                print(f"Exporting {len(self.data)} products to JSON...")
                self._export_data("product_data.json")

                print(f"Successfully extracted {len(self.data)} products.")

            except Exception as e:
                print(f"Error: {e}")
                # Re-raise the exception for debugging
                raise
            finally:
                # Ensure browser is closed even if an error occurs
                browser.close()

        return self.data

    def _load_config(self, config_file="config.json"):
        """
        Load configuration from a JSON file
        """
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {config_file} contains invalid JSON")
                return {}
        else:
            print(f"Warning: {config_file} not found")
            return {}

    def _is_login_required(self, page: Page) -> bool:
        """
        Check if login is required by looking for login indicators
        """
        print("Checking if login is required...")
        login_indicators = [
            "input[type='password']",
            "#login-form",
            "button:has-text('Login')",
            "button:has-text('Sign In')"
        ]

        # Check each selector with a short timeout
        for selector in login_indicators:
            try:
                if page.locator(selector).first.is_visible(timeout=2000):
                    print(f"Login indicator found: {selector}")
                    return True
            except:
                continue
        print("No login required")
        return False

    def _login(self, page: Page, username: str, password: str) -> None:
        """
        Perform login with provided credentials
        """
        print("Attempting login...")
        # Fill username field
        page.fill("input[type='text'], input[type='email'], input[name='username']", username)
        # Fill password field
        page.fill("input[type='password']", password)
        # Click login button
        page.click("button:has-text('Login'), button:has-text('Sign In'), input[type='submit']")
        # Wait for navigation to complete
        page.wait_for_load_state("networkidle")
        time.sleep(5)
        
        # Verify login was successful
        if self._is_login_required(page):
            raise Exception("Login failed - still seeing login form")

    def _navigate_to_products(self, page: Page) -> None:
        """
        Navigate through the menu to reach the products page
        """
        print("Looking for menu button...")
        menu_selectors = [
            "button:has-text('Menu')",
            "[aria-label='Menu']",
            ".menu-button",
            "button[class*='menu']",
            "button:has(svg)",
            "button >> nth=0"
        ]
        
        # Try each menu selector with smart waiting
        for selector in menu_selectors:
            try:
                if self._wait_for_selector(page, selector, timeout=5000):
                    print(f"Found menu: {selector}")
                    page.locator(selector).first.click()
                    break
            except:
                continue
        
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        print("Looking for Data Management option...")
        data_management_selectors = [
            "button:has-text('Data Management')",
            "a:has-text('Data Management')",
            "[href*='data']",
            "[href*='management']",
            "div:has-text('Data Management')"
        ]
        
        # Try each data management selector
        for selector in data_management_selectors:
            try:
                if self._wait_for_selector(page, selector, timeout=5000):
                    print(f"Found Data Management: {selector}")
                    page.locator(selector).first.click()
                    break
            except:
                continue
        
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        print("Looking for Inventory option...")
        inventory_selectors = [
            "button:has-text('Inventory')",
            "a:has-text('Inventory')",
            "[href*='inventory']",
            "div:has-text('Inventory')"
        ]
        
        # Try each inventory selector
        for selector in inventory_selectors:
            try:
                if self._wait_for_selector(page, selector, timeout=5000):
                    print(f"Found Inventory: {selector}")
                    page.locator(selector).first.click()
                    break
            except:
                continue
        
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        print("Looking for View All Products option...")
        view_all_selectors = [
            "button:has-text('View All Products')",
            "a:has-text('View All Products')",
            "button:has-text('View All')",
            "a:has-text('View All')",
            "[href*='product']",
            "[href*='view']"
        ]
        
        # Try each view all selector
        for selector in view_all_selectors:
            try:
                if self._wait_for_selector(page, selector, timeout=10000):
                    print(f"Found View All: {selector}")
                    page.locator(selector).first.click()
                    break
            except:
                continue
        
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        print("Looking for Load Table button...")
        load_table_selectors = [
            "button:has-text('Load Product Table')",
            "button:has-text('Load Table')",
            "button:has-text('Load Products')",
            "button:has-text('Load')",
            "button >> nth=0"
        ]
        
        # Try each load table selector
        for selector in load_table_selectors:
            try:
                if self._wait_for_selector(page, selector, timeout=10000):
                    print(f"Found Load button: {selector}")
                    page.locator(selector).first.click()
                    break
            except:
                continue
        
        page.wait_for_load_state("networkidle")
        time.sleep(5)

    def _wait_for_selector(self, page: Page, selector: str, timeout: int = 10000) -> bool:
        """
        Smart waiting for selector with multiple strategies
        """
        try:
            # Wait for selector to be visible
            page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except TimeoutError:
            # Try alternative approach - check if element exists
            if page.locator(selector).count() > 0:
                return True
            return False

    
        """
        Extract product data from the grid with pagination handling
        """
        print("Waiting for product grid to load...")
        
        # Wait for product cards to appear
        try:
            page.wait_for_selector(".grid > div", state="visible", timeout=20000)
            print("Product grid found")
        except TimeoutError:
            print("Timeout waiting for product grid")
            return
        
        # Use JavaScript to extract data more precisely
        product_data_list = page.evaluate("""
            () => {
                const products = [];
                const cards = document.querySelectorAll('.grid > div');
                
                cards.forEach(card => {
                    try {
                        const product = {};
                        
                        // Extract name from the colored header
                        const nameDiv = card.querySelector('div.h-12');
                        if (nameDiv) {
                            product.name = nameDiv.textContent.trim();
                        }
                        
                        // Extract details from the p-3 container
                        const detailsContainer = card.querySelector('.p-3');
                        if (detailsContainer) {
                            const detailDivs = detailsContainer.querySelectorAll('div.text-xs > div');
                            
                            detailDivs.forEach(div => {
                                const text = div.textContent.trim();
                                
                                if (text.startsWith('ID:')) {
                                    // Get all spans and take the last one which should be the value
                                    const spans = div.querySelectorAll('span');
                                    if (spans.length > 0) {
                                        product.id = spans[spans.length - 1].textContent.trim();
                                    } else {
                                        product.id = text.replace('ID:', '').trim();
                                    }
                                }
                                else if (text.includes('Price')) {
                                    // Look for the price value in spans
                                    const spans = div.querySelectorAll('span');
                                    if (spans.length > 0) {
                                        product.price = spans[spans.length - 1].textContent.trim();
                                    } else {
                                        // Fallback: extract dollar amount
                                        const priceMatch = text.match(/\\$[\\d,]+\\.[\\d]{2}/);
                                        if (priceMatch) {
                                            product.price = priceMatch[0];
                                        }
                                    }
                                }
                                else if (text.includes('Mass (kg)')) {
                                    // Look for the mass value in spans
                                    const spans = div.querySelectorAll('span');
                                    if (spans.length > 0) {
                                        product.mass_kg = spans[spans.length - 1].textContent.trim();
                                    } else {
                                        // Fallback: extract number
                                        const massMatch = text.match(/[\\d.]+/);
                                        if (massMatch) {
                                            product.mass_kg = massMatch[0];
                                        }
                                    }
                                }
                                else if (text.includes('Score')) {
                                    // Look for the score value in spans (usually has ml-1 class)
                                    const scoreSpan = div.querySelector('span.ml-1');
                                    if (scoreSpan) {
                                        product.score = scoreSpan.textContent.trim();
                                    } else {
                                        const spans = div.querySelectorAll('span');
                                        if (spans.length > 0) {
                                            product.score = spans[spans.length - 1].textContent.trim();
                                        } else {
                                            // Fallback: extract number
                                            const scoreMatch = text.match(/[\\d.]+/);
                                            if (scoreMatch) {
                                                product.score = scoreMatch[0];
                                            }
                                        }
                                    }
                                }
                            });
                        }
                        
                        if (product.name && product.id && product.price && product.mass_kg && product.score) {
                            products.push(product);
                        }
                    } catch (e) {
                        console.error('Error processing card:', e);
                    }
                });
                
                return products;
            }
        """)
        
        # Add extracted products to self.data
        extracted_ids = set()
        for product in product_data_list:
            if (product["id"] not in extracted_ids and 
                len(self.data) < (self.max_products or float('inf'))):
                # Clean up the values
                product["id"] = product["id"].split()[0] if " " in product["id"] else product["id"]
                product["price"] = product["price"].split()[0] if " " in product["price"] else product["price"]
                product["mass_kg"] = product["mass_kg"].split()[0] if " " in product["mass_kg"] else product["mass_kg"]
                
                self.data.append(product)
                extracted_ids.add(product["id"])
                print(f"Extracted product {len(self.data)}: {product['name']} (ID: {product['id']})")
        
        print(f"Extracted {len(self.data)} products via JavaScript")
    def _extract_product_data(self, page: Page) -> None:
        """
        Extract product data from the grid with pagination handling
        """
        print("Waiting for product grid to load...")
        
        # Wait for product cards to appear
        try:
            page.wait_for_selector(".grid > div", state="visible", timeout=20000)
            print("Product grid found")
        except TimeoutError:
            print("Timeout waiting for product grid")
            return
        
        # Initialize variables for scroll handling
        last_height = page.evaluate("document.body.scrollHeight")
        extracted_ids = set()
        scroll_attempts = 0
        max_scroll_attempts = 1000  
        no_new_items_count = 0
        max_no_new_items = 3  # Stop after 3 iterations with no new items
        
        print("Starting to extract product data with scrolling...")
        
        # Continue scrolling until max attempts or no new products found
        while scroll_attempts < max_scroll_attempts and no_new_items_count < max_no_new_items:
            if self.max_products and len(self.data) >= self.max_products:
                print(f"Reached maximum products limit: {self.max_products}")
                break
                
            # Extract products from current view
            current_batch_count = len(self.data)
            self._extract_products_from_current_view(page, extracted_ids)
            new_items_in_batch = len(self.data) - current_batch_count
            
            print(f"Batch extracted: {new_items_in_batch} new products, total: {len(self.data)}")
            
            # Check if we found new items in this batch
            if new_items_in_batch == 0:
                no_new_items_count += 1
                print(f"No new items found in this batch. Count: {no_new_items_count}/{max_no_new_items}")
            else:
                no_new_items_count = 0  # Reset counter if we found new items
            
            # Check if we've reached the product limit
            if self.max_products and len(self.data) >= self.max_products:
                break
                
            # Scroll to load more products
            print(f"Scrolling to load more products (attempt {scroll_attempts + 1}/{max_scroll_attempts})...")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)  
            
            # Check if scrolling loaded new content
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                print(f"No new content after scroll. Scroll attempts: {scroll_attempts}/{max_scroll_attempts}")
            else:
                scroll_attempts = 0  # Reset scroll attempts if new content was loaded
                last_height = new_height
                print("New content loaded after scrolling")
                
            # Small delay to avoid overwhelming the page
            time.sleep(1)
        
        print(f"Scrolling completed. Total products extracted: {len(self.data)}")
        if scroll_attempts >= max_scroll_attempts:
            print("Reached maximum scroll attempts (1000)")
        if no_new_items_count >= max_no_new_items:
            print("No new items found for multiple iterations, stopping extraction")

    def _extract_products_from_current_view(self, page: Page, extracted_ids: set) -> None:
        """
        Extract products from the currently visible view
        """
    
        product_data_list = page.evaluate("""
            () => {
                const products = [];
                const cards = document.querySelectorAll('.grid > div');
                
                cards.forEach(card => {
                    try {
                        const product = {};
                        
                        // Extract name from the colored header
                        const nameDiv = card.querySelector('div.h-12');
                        if (nameDiv) {
                            product.name = nameDiv.textContent.trim();
                        }
                        
                        // Extract details from the p-3 container
                        const detailsContainer = card.querySelector('.p-3');
                        if (detailsContainer) {
                            const detailDivs = detailsContainer.querySelectorAll('div.text-xs > div');
                            
                            detailDivs.forEach(div => {
                                const text = div.textContent.trim();
                                
                                if (text.startsWith('ID:')) {
                                    // Get all spans and take the last one which should be the value
                                    const spans = div.querySelectorAll('span');
                                    if (spans.length > 0) {
                                        product.id = spans[spans.length - 1].textContent.trim();
                                    } else {
                                        product.id = text.replace('ID:', '').trim();
                                    }
                                }
                                else if (text.includes('Price')) {
                                    // Look for the price value in spans
                                    const spans = div.querySelectorAll('span');
                                    if (spans.length > 0) {
                                        product.price = spans[spans.length - 1].textContent.trim();
                                    } else {
                                        // Fallback: extract dollar amount
                                        const priceMatch = text.match(/\\$[\\d,]+\\.[\\d]{2}/);
                                        if (priceMatch) {
                                            product.price = priceMatch[0];
                                        } else {
                                            product.price = text.replace('Price', '').trim();
                                        }
                                    }
                                }
                                else if (text.includes('Mass (kg)')) {
                                    // Look for the mass value in spans
                                    const spans = div.querySelectorAll('span');
                                    if (spans.length > 0) {
                                        product.mass_kg = spans[spans.length - 1].textContent.trim();
                                    } else {
                                        // Fallback: extract number
                                        const massMatch = text.match(/[\\d.]+/);
                                        if (massMatch) {
                                            product.mass_kg = massMatch[0];
                                        } else {
                                            product.mass_kg = text.replace('Mass (kg)', '').trim();
                                        }
                                    }
                                }
                                else if (text.includes('Score')) {
                                    // Look for the score value in spans (usually has ml-1 class)
                                    const scoreSpan = div.querySelector('span.ml-1');
                                    if (scoreSpan) {
                                        product.score = scoreSpan.textContent.trim();
                                    } else {
                                        const spans = div.querySelectorAll('span');
                                        if (spans.length > 0) {
                                            product.score = spans[spans.length - 1].textContent.trim();
                                        } else {
                                            // Fallback: extract number
                                            const scoreMatch = text.match(/[\\d.]+/);
                                            if (scoreMatch) {
                                                product.score = scoreMatch[0];
                                            } else {
                                                product.score = text.replace('Score', '').trim();
                                            }
                                        }
                                    }
                                }
                            });
                        }
                        
                        if (product.name && product.id && product.price && product.mass_kg && product.score) {
                            products.push(product);
                        }
                    } catch (e) {
                        console.error('Error processing card:', e);
                    }
                });
                
                return products;
            }
        """)
        
        # Add extracted products to self.data
        for product in product_data_list:
            if (product["id"] not in extracted_ids and 
                len(self.data) < (self.max_products or float('inf'))):
                
        
                product["id"] = self._clean_value(product["id"])
                product["price"] = self._clean_value(product["price"])
                product["mass_kg"] = self._clean_value(product["mass_kg"])
                product["score"] = self._clean_value(product["score"])
                
                self.data.append(product)
                extracted_ids.add(product["id"])

    def _clean_value(self, value: str) -> str:
        """
        Clean extracted values by removing unwanted text and keeping only the relevant part
        """
        
        if " " in value:
            parts = value.split()
            # Try to find the part that looks like a value (number, dollar amount, etc.)
            for part in parts:
                if any(char.isdigit() for char in part) or part.startswith('$'):
                    return part
            return parts[0]  # Fallback to first part
        return value
    
    def _export_data(self, filename: str) -> None:
        """
        Export extracted data to a JSON file
        """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"Data exported to {filename}")


if __name__ == "__main__":
    # Configuration
    APP_URL = "https://hiring.idenhq.com/"
    
    # Create extractor instance
    extractor = DataExtractor(APP_URL)
    
    # Run extraction process
    data = extractor.run()
    
    # Print results
    print(f"Extracted {len(data)} products.")
    if data:
        print("Sample product:")
        print(json.dumps(data[0], indent=2))
