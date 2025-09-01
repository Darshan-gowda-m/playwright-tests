# 🛠️ IDENHQ Challenge Data Extractor

This project is a **web data extraction tool** built with [Playwright](https://playwright.dev/python/) in Python.  
It automates login, navigates through the **challenge → products section**, and extracts structured product data into JSON.  
Screenshots are also captured along the way for debugging.

---

## ✨ Features
- 🔑 Handles login automatically (saves session for reuse).
- 📸 Takes screenshots for debugging (`debug/` folder).
- 📂 Navigates menus → **Data Management → Inventory → View All Products**.
- 📊 Extracts:
  - Product **ID**
  - **Name**
  - **Price**
  - **Mass (kg)**
  - **Score**
- ⏳ Infinite scroll support (keeps loading products until none left).
- 🎯 Option to limit extraction to **N products**.
- 💾 Exports results into **JSON** (`product_data.json`).

---

## 🚀 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/idenhq-extractor.git
   cd idenhq-extractor
   ```

   ### Install dependencies:
   ```bash
   pip install playwright
   playwright install
   ```

   ### ▶️ Usage

   Run the extractor:
   ```bash
   python extractor.py
   ```

   ### 🏗️ Tech Stack

    Python 3.9+

    Playwright


   ### in main
   if __name__ == "__main__":
    APP_URL = "https://hiring.idenhq.com/"
    USERNAME = "your_email@example.com"
    PASSWORD = "your_password"

    extractor = DataExtractor(APP_URL)

    # Extract all products (or limit with max_products=50)
    data = extractor.run(USERNAME, PASSWORD, max_products=50)

    print(f"Extracted {len(data)} products.")
    if data:
        print("Sample product:")
        print(json.dumps(data[0], indent=2))


   ### 📂 Output

    Product data → product_data.json

    Screenshots → debug/































