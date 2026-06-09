# AI Shopping Agent

A smart desktop application that helps Pakistani online shoppers compare product prices across **Daraz**, **Goto**, and **Shophive** simultaneously — powered by Python, MongoDB, and Selenium.

##  Features

-  Search any product across 3 websites at once
-  Side-by-side price comparison
-  Auto-detects the best (cheapest) deal
-  Save favorite products to MongoDB
-  Full search history with smart caching
-  Analytics dashboard — stats, trends, category insights

---

##  Technologies

| Technology | Purpose |
|------------|---------|
| Python 3.x | Core application language |
| MongoDB | NoSQL database backend |
| PyMongo | Python ↔ MongoDB driver |
| Selenium | Headless web scraping |
| CustomTkinter | Modern desktop GUI |
| Threading | Parallel scraping (3 sites at once) |

---

##  Project Structure
ai-shopping-agent/
│
├── main.py          # GUI application (CustomTkinter)
├── scraper.py       # Selenium scrapers for all 3 websites
├── database.py      # All MongoDB CRUD + aggregation operations
├── Seeddata.py      # Populate MongoDB with demo products
└── requirements.txt # Python dependencies


---

##  Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-shopping-agent.git
cd ai-shopping-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Make sure MongoDB is running
```bash
# Windows
net start MongoDB

# Or start manually
mongod
```

### 4. Seed the database with demo data
```bash
python Seeddata.py
```

### 5. Run the app
```bash
python main.py
```

---

##  requirements.txt
pymongo
selenium
webdriver-manager
customtkinter

---

##  Database Design

**Database:** `shopping_agent`

| Collection | Fields |
|------------|--------|
| `all_products` | name, price, price_display, website, category, link, saved_at |
| `search_history` | product, date, time |
| `favorite_products` | product, price, price_numeric, website, link, date |



