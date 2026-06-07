"""
Seeddata.py  —  Run once to populate MongoDB with demo products.
Usage:  python Seeddata.py
"""
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db     = client["shopping_agent"]

products_col  = db["all_products"]
searches_col  = db["search_history"]
favorites_col = db["favorite_products"]

# ── helpers ──────────────────────────────────────────────────────────────────
def ts(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def add(name, price, website, category, link):
    if products_col.find_one({"name": name, "website": website}):
        return
    products_col.insert_one({
        "name":          name,
        "price":         price,               # stored as int always
        "price_display": f"Rs. {price:,}",
        "website":       website,
        "category":      category,
        "link":          link,
        "saved_at":      ts()
    })

# ── MOBILES ──────────────────────────────────────────────────────────────────
mobiles = [
    # Daraz
    ("Samsung Galaxy A55 5G 8GB/256GB",          89999, "Daraz",    "https://www.daraz.pk/products/samsung-galaxy-a55.html"),
    ("Samsung Galaxy A35 5G 6GB/128GB",          64999, "Daraz",    "https://www.daraz.pk/products/samsung-galaxy-a35.html"),
    ("iPhone 15 128GB Black",                   289999, "Daraz",    "https://www.daraz.pk/products/iphone-15.html"),
    ("Xiaomi Redmi Note 13 Pro 8GB/256GB",       62999, "Daraz",    "https://www.daraz.pk/products/redmi-note-13-pro.html"),
    ("Vivo V29e 8GB/256GB",                      59999, "Daraz",    "https://www.daraz.pk/products/vivo-v29e.html"),
    ("OPPO A78 8GB/128GB",                       52999, "Daraz",    "https://www.daraz.pk/products/oppo-a78.html"),
    ("Tecno Spark 20 Pro 8GB/256GB",             34999, "Daraz",    "https://www.daraz.pk/products/tecno-spark-20-pro.html"),
    ("Infinix Hot 40 Pro 8GB/256GB",             32999, "Daraz",    "https://www.daraz.pk/products/infinix-hot-40-pro.html"),
    # Goto
    ("Samsung Galaxy S24 8GB/256GB",            249999, "Goto",     "https://www.goto.com.pk/samsung-galaxy-s24.html"),
    ("iPhone 14 128GB Midnight",                219999, "Goto",     "https://www.goto.com.pk/iphone-14.html"),
    ("Xiaomi 14T Pro 12GB/512GB",               139999, "Goto",     "https://www.goto.com.pk/xiaomi-14t-pro.html"),
    ("OnePlus 12R 8GB/128GB",                    99999, "Goto",     "https://www.goto.com.pk/oneplus-12r.html"),
    ("Realme 12 Pro+ 8GB/256GB",                 79999, "Goto",     "https://www.goto.com.pk/realme-12-pro-plus.html"),
    ("Nokia G42 5G 6GB/128GB",                   39999, "Goto",     "https://www.goto.com.pk/nokia-g42.html"),
    ("Motorola Moto G85 8GB/256GB",              54999, "Goto",     "https://www.goto.com.pk/moto-g85.html"),
    # Shophive
    ("Samsung Galaxy A15 4GB/128GB",             34999, "Shophive", "https://www.shophive.com/samsung-galaxy-a15.html"),
    ("iPhone 13 128GB Starlight",               179999, "Shophive", "https://www.shophive.com/iphone-13.html"),
    ("Xiaomi Redmi 13C 4GB/128GB",               24999, "Shophive", "https://www.shophive.com/redmi-13c.html"),
    ("OPPO Reno 11 F 8GB/256GB",                 69999, "Shophive", "https://www.shophive.com/oppo-reno-11f.html"),
    ("Huawei Nova 11 8GB/256GB",                 74999, "Shophive", "https://www.shophive.com/huawei-nova-11.html"),
    ("Google Pixel 8a 8GB/128GB",               129999, "Shophive", "https://www.shophive.com/pixel-8a.html"),
]

# ── LAPTOPS ──────────────────────────────────────────────────────────────────
laptops = [
    # Daraz
    ("Dell Inspiron 15 Core i5 13th Gen 8GB/512GB",  119999, "Daraz",    "https://www.daraz.pk/products/dell-inspiron-15.html"),
    ("HP Pavilion 15 Core i7 8GB/512GB SSD",         134999, "Daraz",    "https://www.daraz.pk/products/hp-pavilion-15.html"),
    ("Lenovo IdeaPad Slim 5 Ryzen 5 16GB/512GB",     109999, "Daraz",    "https://www.daraz.pk/products/lenovo-ideapad-slim5.html"),
    ("ASUS VivoBook 15 Core i5 8GB/256GB",            94999, "Daraz",    "https://www.daraz.pk/products/asus-vivobook-15.html"),
    ("Acer Aspire 5 Core i3 8GB/512GB",               79999, "Daraz",    "https://www.daraz.pk/products/acer-aspire-5.html"),
    # Goto
    ("Dell XPS 15 Core i7 13th 16GB/1TB",            299999, "Goto",     "https://www.goto.com.pk/dell-xps-15.html"),
    ("HP Spectre x360 Core i7 16GB/1TB",             289999, "Goto",     "https://www.goto.com.pk/hp-spectre-x360.html"),
    ("Lenovo ThinkPad E14 Core i5 16GB/512GB",       159999, "Goto",     "https://www.goto.com.pk/thinkpad-e14.html"),
    ("MacBook Air M2 8GB/256GB Space Gray",          319999, "Goto",     "https://www.goto.com.pk/macbook-air-m2.html"),
    ("MSI Thin GF63 Core i5 RTX 4050 8GB/512GB",    164999, "Goto",     "https://www.goto.com.pk/msi-thin-gf63.html"),
    # Shophive
    ("Apple MacBook Pro M3 14-inch 8GB/512GB",       499999, "Shophive", "https://www.shophive.com/macbook-pro-m3.html"),
    ("ASUS ROG Strix G16 Core i9 RTX 4060 32GB",    389999, "Shophive", "https://www.shophive.com/asus-rog-strix-g16.html"),
    ("HP Victus 15 Core i5 RTX 3050 8GB/512GB",     134999, "Shophive", "https://www.shophive.com/hp-victus-15.html"),
    ("Lenovo Legion 5 Ryzen 7 RTX 4060 16GB",       219999, "Shophive", "https://www.shophive.com/lenovo-legion-5.html"),
    ("Acer Nitro 5 Core i7 RTX 4050 16GB/512GB",    179999, "Shophive", "https://www.shophive.com/acer-nitro-5.html"),
]

# ── HEADPHONES ───────────────────────────────────────────────────────────────
headphones = [
    ("Sony WH-1000XM5 Wireless ANC",              79999, "Daraz",    "https://www.daraz.pk/products/sony-wh1000xm5.html"),
    ("JBL Tune 770NC Wireless",                   24999, "Daraz",    "https://www.daraz.pk/products/jbl-tune-770nc.html"),
    ("Bose QuietComfort 45 Wireless ANC",          89999, "Goto",     "https://www.goto.com.pk/bose-qc45.html"),
    ("Apple AirPods Pro 2nd Generation",           89999, "Goto",     "https://www.goto.com.pk/airpods-pro-2.html"),
    ("Samsung Galaxy Buds2 Pro",                   34999, "Shophive", "https://www.shophive.com/galaxy-buds2-pro.html"),
    ("Sennheiser HD 450BT Wireless",               29999, "Shophive", "https://www.shophive.com/sennheiser-hd450bt.html"),
]

# ── TVs ──────────────────────────────────────────────────────────────────────
tvs = [
    ("Samsung 55 inch 4K QLED Smart TV",          159999, "Daraz",    "https://www.daraz.pk/products/samsung-55-qled.html"),
    ("TCL 65 inch 4K Android TV",                  99999, "Goto",     "https://www.goto.com.pk/tcl-65-4k.html"),
    ("Haier 43 inch Full HD Android TV",           59999, "Shophive", "https://www.shophive.com/haier-43-fhd.html"),
    ("Sony Bravia 55 inch 4K Google TV",          189999, "Shophive", "https://www.shophive.com/sony-bravia-55.html"),
]

# ── ACs ──────────────────────────────────────────────────────────────────────
acs = [
    ("Dawlance Inverter 1.5 Ton Elegance",         94999, "Daraz",    "https://www.daraz.pk/products/dawlance-15ton.html"),
    ("Gree 1 Ton Inverter Pular Series",           79999, "Goto",     "https://www.goto.com.pk/gree-1ton-pular.html"),
    ("Haier 1.5 Ton Turbo Cool Inverter",          89999, "Shophive", "https://www.shophive.com/haier-15ton.html"),
    ("PEL 2 Ton Inverter Arctic",                 119999, "Daraz",    "https://www.daraz.pk/products/pel-2ton-arctic.html"),
]

# ── INSERT ALL ────────────────────────────────────────────────────────────────
all_products = (
    [(p[0], p[1], p[2], "Mobile",      p[3]) for p in mobiles]    +
    [(p[0], p[1], p[2], "Laptop",      p[3]) for p in laptops]    +
    [(p[0], p[1], p[2], "Headphones",  p[3]) for p in headphones] +
    [(p[0], p[1], p[2], "TV",          p[3]) for p in tvs]        +
    [(p[0], p[1], p[2], "AC",          p[3]) for p in acs]
)

inserted = 0
for name, price, website, category, link in all_products:
    add(name, price, website, category, link)
    inserted += 1

# ── SEARCH HISTORY ────────────────────────────────────────────────────────────
for query in ["mobile", "laptop", "headphones", "TV", "AC"]:
    if not searches_col.find_one({"product": query}):
        searches_col.insert_one({
            "product": query,
            "date":    datetime.now().strftime("%Y-%m-%d"),
            "time":    datetime.now().strftime("%H:%M:%S"),
        })

# ── FAVORITES ─────────────────────────────────────────────────────────────────
# BUG FIX: favorites now store both price_display (string) AND price_numeric (int)
# so they can be displayed AND sorted/compared correctly.
favs = [
    ("Samsung Galaxy A55 5G 8GB/256GB",   "Rs. 89,999",   89999,  "Daraz",    "https://www.daraz.pk/products/samsung-galaxy-a55.html"),
    ("MacBook Air M2 8GB/256GB",          "Rs. 319,999",  319999, "Goto",     "https://www.goto.com.pk/macbook-air-m2.html"),
    ("Sony WH-1000XM5 Wireless ANC",      "Rs. 79,999",   79999,  "Daraz",    "https://www.daraz.pk/products/sony-wh1000xm5.html"),
]
for name, price_display, price_numeric, website, link in favs:
    if not favorites_col.find_one({"product": name}):
        favorites_col.insert_one({
            "product":       name,
            "price":         price_display,    # human-readable string
            "price_numeric": price_numeric,    # integer for sorting/comparison
            "website":       website,
            "link":          link,
            "date":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

# ── SUMMARY ───────────────────────────────────────────────────────────────────
total = products_col.count_documents({})
print(f"\n✅  Done! MongoDB now has {total} products total.")
print(f"   Mobiles:    {products_col.count_documents({'category': 'Mobile'})}")
print(f"   Laptops:    {products_col.count_documents({'category': 'Laptop'})}")
print(f"   Headphones: {products_col.count_documents({'category': 'Headphones'})}")
print(f"   TVs:        {products_col.count_documents({'category': 'TV'})}")
print(f"   ACs:        {products_col.count_documents({'category': 'AC'})}")
print(f"\n   Search History: {searches_col.count_documents({})}")
print(f"   Favorites:      {favorites_col.count_documents({})}")
print("\n▶  Now run:  python main.py")