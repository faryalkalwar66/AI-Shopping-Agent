from pymongo import MongoClient
from datetime import datetime

# ==========================================
#       MONGODB CONNECTION
# ==========================================

client = MongoClient("mongodb://localhost:27017/")
db     = client["shopping_agent"]

# Collections
searches_col  = db["search_history"]
products_col  = db["all_products"]
favorites_col = db["favorite_products"]


# ==========================================
#       CREATE — SAVE FUNCTIONS
# ==========================================

def save_search(product_name):
    """Save a search query to MongoDB."""
    now = datetime.now()
    searches_col.insert_one({
        "product": product_name,
        "date":    now.strftime("%Y-%m-%d"),
        "time":    now.strftime("%H:%M:%S"),
    })


def save_product(name, price, price_display, website, category, link):
    """Save a scraped product to MongoDB (no duplicates)."""
    existing = products_col.find_one({"name": name, "website": website})
    if existing:
        # UPDATE price if changed
        products_col.update_one(
            {"_id": existing["_id"]},
            {"$set": {"price": price, "price_display": price_display,
                      "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
        )
    else:
        products_col.insert_one({
            "name":          name,
            "price":         price,          # always stored as int
            "price_display": price_display,
            "website":       website,
            "category":      category,
            "link":          link,
            "saved_at":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })


def save_favorite(name, price_display, price_numeric, website, link):
    """Add a product to favorites.
    
    BUG FIX: now stores both price_display (string, e.g. 'Rs. 89,999')
    AND price_numeric (int) so favorites can be sorted/compared by price.
    """
    favorites_col.insert_one({
        "product":       name,
        "price":         price_display,    # human-readable string for display
        "price_numeric": price_numeric,    # integer for sorting/comparison
        "website":       website,
        "link":          link,
        "date":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })


# ==========================================
#       READ — GET FUNCTIONS
# ==========================================

def search_exists(product_name):
    """Check if a search was done before."""
    return searches_col.find_one({"product": product_name}) is not None


def is_already_favorite(name):
    """Check if product is already in favorites."""
    return favorites_col.find_one({"product": name}) is not None


def get_all_searches():
    """Return all search history, newest first."""
    return list(searches_col.find({}, {"_id": 0}).sort("_id", -1))


def get_all_favorites():
    """Return all favorite products."""
    return list(favorites_col.find({}, {"_id": 0}))


def get_all_products():
    """Return all products from MongoDB."""
    return list(products_col.find({}, {"_id": 0}))


def get_products_by_category(category):
    """Return products filtered by category."""
    if category == "All":
        return get_all_products()
    return list(products_col.find({"category": category}, {"_id": 0}))


def search_products_db(product_name):
    """Search products by name in MongoDB (case-insensitive)."""
    results = products_col.find(
        {"name": {"$regex": product_name, "$options": "i"}},
        {"_id": 0}
    )
    return list(results)


def compare_prices(product_name):
    """Compare prices for a product across websites."""
    results = search_products_db(product_name)
    by_website = {}
    for r in results:
        site = r.get("website", "Unknown")
        if site not in by_website:
            by_website[site] = []
        by_website[site].append(r)
    return by_website


def get_best_deal(product_name):
    """Get the cheapest product for a given search."""
    results = search_products_db(product_name)
    if not results:
        return None
    return min(results, key=lambda x: x.get("price", 999999))


def get_best_deals_all():
    """Get best (cheapest) product from each website."""
    pipeline = [
        {"$group": {
            "_id":       "$website",
            "min_price": {"$min": "$price"},
            "product":   {"$first": "$name"},
            "link":      {"$first": "$link"},
        }}
    ]
    return list(products_col.aggregate(pipeline))


def get_savings_comparison():
    """Compare cheapest vs most expensive per product category."""
    pipeline = [
        {"$group": {
            "_id":       "$category",
            "min_price": {"$min": "$price"},
            "max_price": {"$max": "$price"},
            "avg_price": {"$avg": "$price"},
            "count":     {"$sum": 1},
        }}
    ]
    return list(products_col.aggregate(pipeline))


def get_website_stats():
    """Aggregate stats per website using MongoDB pipeline."""
    pipeline = [
        {"$group": {
            "_id":            "$website",
            "avg_price":      {"$avg": "$price"},
            "cheapest":       {"$min": "$price"},
            "most_expensive": {"$max": "$price"},
            "total_products": {"$sum": 1},
        }}
    ]
    return list(products_col.aggregate(pipeline))


def count_products_per_website():
    """Count products per website."""
    result = {}
    for website in ["Daraz", "Goto", "Shophive"]:
        result[website] = products_col.count_documents({"website": website})
    return result


def count_searches():
    return searches_col.count_documents({})


def count_favorites():
    return favorites_col.count_documents({})


def get_stats():
    """Return summary statistics."""
    return {
        "total_products":  products_col.count_documents({}),
        "total_searches":  searches_col.count_documents({}),
        "total_favorites": favorites_col.count_documents({}),
    }


# ==========================================
#       UPDATE FUNCTIONS
# ==========================================

def update_favorite_price(name, new_price_display, new_price_numeric):
    """Update price of a saved favorite.
    
    BUG FIX: updates both price (display string) and price_numeric (int).
    """
    favorites_col.update_one(
        {"product": name},
        {"$set": {
            "price":         new_price_display,
            "price_numeric": new_price_numeric,
            "updated_at":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }}
    )


def update_product_category(name, website, new_category):
    """Update product category."""
    products_col.update_one(
        {"name": name, "website": website},
        {"$set": {"category": new_category}}
    )


# ==========================================
#       DELETE FUNCTIONS
# ==========================================

def delete_all_searches():
    """Clear all search history."""
    searches_col.delete_many({})


def delete_all_favorites():
    """Clear all favorites."""
    favorites_col.delete_many({})


def delete_product(name, website):
    """Delete a specific product."""
    products_col.delete_one({"name": name, "website": website})


def delete_favorite(name):
    """Delete a specific favorite by product name."""
    favorites_col.delete_one({"product": name})