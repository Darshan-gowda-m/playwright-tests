# 🛠️ IDENHQ Challenge Data Extractor

A **web data extraction tool** built with [Playwright](https://playwright.dev/python/) in Python.  
It automates login, navigates through the **Challenge → Products** section, and extracts structured product data into JSON.  

---

## ✨ Features
- 🔑 Automatic login (saves session for reuse).
- ⚙️ Supports `config.json` for credentials.
- 📂 Navigates menus → **Data Management → Inventory → View All Products**.
- 📊 Extracts:
  - Product **ID**
  - **Name**
  - **Price**
  - **Mass (kg)**
  - **Score**
- ⏳ Infinite scroll support (keeps loading until no more products).
- 🎯 Default extraction limit → **All products**  
  (customizable: change the value of `max_products` in `extractor.run()`)

- 💾 Exports results into **`product_data.json`**.
  
---

## 🚀 Installation

Clone the repository:
```bash
git clone https://github.com/Darshan-gowda-m/playwright-tests.git
cd playwright-tests
```

## Install dependencies:
```bash
pip install playwright
playwright install
```

### ⚙️ Configuration

You can store login credentials in a config.json file.

```json
{
  "username": "your_email@example.com",
  "password": "your_password"
}
```

### ▶️ Usage

Run the extractor:
```bash
python extractor.py
```

### 📂 Output

Extracted product data → product_data.json

### 🏗️ Tech Stack

🐍 Python 3.9+

🎭 Playwright

### 📜 License

This project is licensed under the MIT License – see the LICENSE
 file for details.

 ```java
MIT License  
Copyright (c) 2025 Dharshan Gowda M
```
