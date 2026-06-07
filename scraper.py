from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from database import (save_search, save_product, search_exists,
                      compare_prices, get_best_deal, search_products_db,
                      save_favorite, is_already_favorite)
import threading
import time


# ==========================================
#       CHROME DRIVER SETUP
# ==========================================

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-images")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--disable-extensions")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.set_page_load_timeout(25)
    return driver


# ==========================================
#       CATEGORY DETECTOR
#       BUG FIX: was always saving "General"
# ==========================================

def detect_category(product_name):
    """Detect product category from search term."""
    name = product_name.lower()
    if any(w in name for w in ["mobile", "phone", "iphone", "samsung galaxy",
                                "xiaomi", "oppo", "vivo", "realme", "nokia",
                                "oneplus", "pixel", "huawei", "infinix",
                                "tecno", "motorola"]):
        return "Mobile"
    if any(w in name for w in ["laptop", "macbook", "notebook", "chromebook",
                                "dell", "hp pavilion", "lenovo", "asus vivobook",
                                "acer aspire", "thinkpad", "spectre", "xps",
                                "ideapad", "legion", "rog", "nitro", "victus"]):
        return "Laptop"
    if any(w in name for w in ["headphone", "earphone", "earbud", "airpod",
                                "earpiece", "headset", "buds", "wh-", "jbl",
                                "bose", "sennheiser", "sony wh"]):
        return "Headphones"
    if any(w in name for w in ["tv", "television", "smart tv", "qled", "oled",
                                "android tv", "google tv", "4k tv"]):
        return "TV"
    if any(w in name for w in ["ac", "air conditioner", "inverter ac",
                                "split ac", "dawlance", "gree", "haier ac",
                                "pel", "carrier"]):
        return "AC"
    return "General"


# ==========================================
#       SCRAPE DARAZ
# ==========================================

def scrape_daraz(product_name, results_dict):
    driver = None
    try:
        print("  [Daraz] Starting...")
        driver = create_driver()
        query    = product_name.replace(" ", "+")
        url      = f"https://www.daraz.pk/catalog/?q={query}"
        category = detect_category(product_name)  # BUG FIX: detect proper category

        # BUG FIX: proper retry with delay and fresh driver
        loaded = False
        for attempt in range(2):
            try:
                driver.get(url)
                loaded = True
                break
            except Exception:
                if attempt == 0:
                    print("  [Daraz] Timeout on first attempt, retrying in 3s...")
                    time.sleep(3)
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    driver = create_driver()

        if not loaded:
            results_dict["Daraz"] = []
            return

        time.sleep(5)

        products_data = driver.execute_script(r"""
            var items = document.querySelectorAll('[data-qa-locator="product-item"]');
            var results = [];
            items.forEach(function(item) {
                try {
                    var img  = item.querySelector('img');
                    var name = img ? img.getAttribute('alt') : null;
                    if (!name || name.length < 3) {
                        var divs = item.querySelectorAll('div, span');
                        for (var d of divs) {
                            var txt = d.innerText ? d.innerText.trim() : '';
                            if (txt.length > 8 && !txt.includes('Rs.')
                                && !txt.includes('%')) {
                                name = txt; break;
                            }
                        }
                    }
                    var price_text = 'No price';
                    var price_num  = 0;
                    var spans = item.querySelectorAll('span');
                    for (var s of spans) {
                        var t = s.innerText ? s.innerText.trim() : '';
                        if (t.includes('Rs.')) {
                            price_text = t;
                            price_num  = parseInt(t.replace(/[^0-9]/g, '')) || 0;
                            break;
                        }
                    }
                    var link = '';
                    var a    = item.querySelector('a');
                    if (a && a.href) link = a.href;
                    if (name && name.length > 3 && price_num > 0)
                        results.push({name: name, price_display: price_text,
                                      price: price_num, link: link});
                } catch(e) {}
            });
            return results.slice(0, 8);
        """)

        items = []
        for item in products_data:
            r = {
                "name":          item.get("name", ""),
                "price":         item.get("price", 0),
                "price_display": item.get("price_display", "No price"),
                "website":       "Daraz",
                "category":      category,   # BUG FIX: use detected category
                "link":          item.get("link", ""),
            }
            items.append(r)
            if r["name"] and r["price"] > 0:
                save_product(r["name"], r["price"], r["price_display"],
                             "Daraz", category, r["link"])

        results_dict["Daraz"] = items
        print(f"  [Daraz] Done — {len(items)} products")

    except Exception as e:
        err = str(e)
        if "offline" in err.lower() or "reach host" in err.lower() or "net::" in err.lower():
            print("  [Daraz] Network error — check your internet connection")
        else:
            print(f"  [Daraz] Error: {err[:120]}")
        results_dict["Daraz"] = []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


# ==========================================
#       SCRAPE GOTO
# ==========================================

def scrape_goto(product_name, results_dict):
    driver = None
    try:
        print("  [Goto] Starting...")
        driver   = create_driver()
        query    = product_name.replace(" ", "+")
        url      = f"https://www.goto.com.pk/search?q={query}"
        category = detect_category(product_name)  # BUG FIX: detect proper category

        # BUG FIX: proper retry with delay and fresh driver
        loaded = False
        for attempt in range(2):
            try:
                driver.get(url)
                loaded = True
                break
            except Exception:
                if attempt == 0:
                    print("  [Goto] Timeout on first attempt, retrying in 3s...")
                    time.sleep(3)
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    driver = create_driver()

        if not loaded:
            results_dict["Goto"] = []
            return

        time.sleep(5)

        products_data = driver.execute_script(r"""
            var results = [];
            var selectors = ['.product-item', '.product-card',
                             '[class*="product"]', 'li.item'];
            var items = [];
            for (var sel of selectors) {
                items = document.querySelectorAll(sel);
                if (items.length > 2) break;
            }
            items.forEach(function(item) {
                try {
                    var name = '';
                    var nameEl = item.querySelector(
                        'h2,h3,h4,.title,.name,[class*="title"],[class*="name"]');
                    if (nameEl) name = nameEl.innerText.trim();
                    if (!name) {
                        var img = item.querySelector('img');
                        if (img) name = img.getAttribute('alt') || '';
                    }
                    var price_text = 'No price';
                    var price_num  = 0;
                    var allText    = item.innerText || '';
                    var pm = allText.match(/Rs[.]?\s*[\d,]+/);
                    if (pm) {
                        price_text = pm[0].trim();
                        price_num  = parseInt(price_text.replace(/[^0-9]/g, '')) || 0;
                    }
                    var link = '';
                    var a    = item.querySelector('a');
                    if (a && a.href) link = a.href;
                    if (name && name.length > 3 && price_num > 0)
                        results.push({name: name, price_display: price_text,
                                      price: price_num, link: link});
                } catch(e) {}
            });
            return results.slice(0, 8);
        """)

        items = []
        for item in products_data:
            r = {
                "name":          item.get("name", ""),
                "price":         item.get("price", 0),
                "price_display": item.get("price_display", "No price"),
                "website":       "Goto",
                "category":      category,   # BUG FIX: use detected category
                "link":          item.get("link", ""),
            }
            items.append(r)
            if r["name"] and r["price"] > 0:
                save_product(r["name"], r["price"], r["price_display"],
                             "Goto", category, r["link"])

        results_dict["Goto"] = items
        print(f"  [Goto] Done — {len(items)} products")

    except Exception as e:
        err = str(e)
        if "offline" in err.lower() or "reach host" in err.lower() or "net::" in err.lower():
            print("  [Goto] Network error — check your internet connection")
        else:
            print(f"  [Goto] Error: {err[:120]}")
        results_dict["Goto"] = []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


# ==========================================
#       SCRAPE SHOPHIVE
# ==========================================

def scrape_shophive(product_name, results_dict):
    driver = None
    try:
        print("  [Shophive] Starting...")
        driver   = create_driver()
        query    = product_name.replace(" ", "+")
        url      = f"https://www.shophive.com/search?q={query}"
        category = detect_category(product_name)  # BUG FIX: detect proper category

        # BUG FIX: proper retry with delay and fresh driver
        loaded = False
        for attempt in range(2):
            try:
                driver.get(url)
                loaded = True
                break
            except Exception:
                if attempt == 0:
                    print("  [Shophive] Timeout on first attempt, retrying in 3s...")
                    time.sleep(3)
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    driver = create_driver()

        if not loaded:
            results_dict["Shophive"] = []
            return

        time.sleep(5)

        products_data = driver.execute_script(r"""
            var results = [];
            var selectors = ['.product-item', '.product-card',
                             '.product', '[class*="product"]', 'li.item'];
            var items = [];
            for (var sel of selectors) {
                items = document.querySelectorAll(sel);
                if (items.length > 2) break;
            }
            items.forEach(function(item) {
                try {
                    var name = '';
                    var nameEl = item.querySelector(
                        'h2,h3,h4,.product-name,.title,[class*="name"]');
                    if (nameEl) name = nameEl.innerText.trim();
                    if (!name) {
                        var img = item.querySelector('img');
                        if (img) name = img.getAttribute('alt') || '';
                    }
                    var price_text = 'No price';
                    var price_num  = 0;
                    var allText    = item.innerText || '';
                    var pm = allText.match(/Rs[.]?\s*[\d,]+/);
                    if (pm) {
                        price_text = pm[0].trim();
                        price_num  = parseInt(price_text.replace(/[^0-9]/g, '')) || 0;
                    }
                    var link = '';
                    var a    = item.querySelector('a');
                    if (a && a.href) link = a.href;
                    if (name && name.length > 3 && price_num > 0)
                        results.push({name: name, price_display: price_text,
                                      price: price_num, link: link});
                } catch(e) {}
            });
            return results.slice(0, 8);
        """)

        items = []
        for item in products_data:
            r = {
                "name":          item.get("name", ""),
                "price":         item.get("price", 0),
                "price_display": item.get("price_display", "No price"),
                "website":       "Shophive",
                "category":      category,   # BUG FIX: use detected category
                "link":          item.get("link", ""),
            }
            items.append(r)
            if r["name"] and r["price"] > 0:
                save_product(r["name"], r["price"], r["price_display"],
                             "Shophive", category, r["link"])

        results_dict["Shophive"] = items
        print(f"  [Shophive] Done — {len(items)} products")

    except Exception as e:
        err = str(e)
        if "offline" in err.lower() or "reach host" in err.lower() or "net::" in err.lower():
            print("  [Shophive] Network error — check your internet connection")
        else:
            print(f"  [Shophive] Error: {err[:120]}")
        results_dict["Shophive"] = []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


# ==========================================
#    MAIN SEARCH — 3 WEBSITES PARALLEL
# ==========================================

def search_all_websites(product_name):
    print(f"\nSearching: '{product_name}' on 3 websites PARALLEL...")

    if search_exists(product_name):
        print(f"[MongoDB] '{product_name}' searched before — checking cache...")
    else:
        save_search(product_name)

    # --- Check MongoDB cache first ---
    db_results = search_products_db(product_name)
    if len(db_results) >= 5:
        print(f"[MongoDB] Found {len(db_results)} cached results — skipping scrape!")
        return db_results

    print("[Scraper] Not enough cached data — scraping all 3 websites now...")

    # --- Parallel scraping ---
    results_dict = {"Daraz": [], "Goto": [], "Shophive": []}
    t1 = threading.Thread(target=scrape_daraz,    args=(product_name, results_dict))
    t2 = threading.Thread(target=scrape_goto,     args=(product_name, results_dict))
    t3 = threading.Thread(target=scrape_shophive, args=(product_name, results_dict))

    t1.start(); t2.start(); t3.start()
    t1.join();  t2.join();  t3.join()

    all_results = (results_dict["Daraz"] +
                   results_dict["Goto"]  +
                   results_dict["Shophive"])

    if not all_results:
        print("[MongoDB] Scraping failed (network issue?) — using saved data instead")
        all_results = db_results

    print(f"Total: {len(all_results)} products found")
    return all_results


# ==========================================
#    HELPER WRAPPERS
# ==========================================

def search_products(product_name):
    """Alias kept for backward compatibility."""
    return search_all_websites(product_name)


def get_comparison(product_name):
    return compare_prices(product_name)


def get_best(product_name):
    return get_best_deal(product_name)


def add_to_favorites(name, price_display, price_numeric, website, link):
    """Save product to favorites. Returns True on success, False if duplicate.
    
    BUG FIX: now accepts price_numeric separately so both display string
    and sortable integer are stored in MongoDB.
    """
    if is_already_favorite(name):
        print(f"[MongoDB] Already in favorites: {name}")
        return False
    save_favorite(name, price_display, price_numeric, website, link)
    return True


# ---- TEST ----
if __name__ == "__main__":
    product = input("Enter product to search: ")
    results = search_all_websites(product)
    print(f"\n====== {len(results)} products ======")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['name'][:50]} | {r.get('price_display','')} | {r.get('website','')}")