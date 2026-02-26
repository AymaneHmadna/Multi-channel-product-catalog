import random
from pymongo import MongoClient
from datetime import datetime
print("Tentative de connexion...")
try:
    client = MongoClient('mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000')
    client.admin.command('ping')
    db = client['Catalogue_produits_multi_canaux']
    collection = db['products']
    audit = db['audit']
    print("SUCCESS: Connecté à mongodb")
except Exception as e:
    print(f"ECHEC: Impossible de se connecter. Erreur : {e}")
    exit()
collection.delete_many({})
audit.delete_many({})
print("Database Cleared.")
electronics_db = {
    "Apple": [
        {"name": "iPhone 15 Pro", "price": (999, 1100), "storage": ["128GB", "256GB", "512GB"]},
        {"name": "iPhone 15 Pro Max", "price": (1199, 1599), "storage": ["256GB", "512GB", "1TB"]},
        {"name": "MacBook Air M2", "price": (1099, 1299), "storage": ["256GB", "512GB"]},
        {"name": "MacBook Pro 16 M3 Max", "price": (3499, 3999), "storage": ["1TB", "2TB", "4TB"]},
        {"name": "iPad Pro 12.9", "price": (1099, 1399), "storage": ["128GB", "256GB", "1TB"]},
        {"name": "Apple Watch Ultra 2", "price": (799, 799), "storage": ["64GB"]},
        {"name": "AirPods Pro (2nd Gen)", "price": (249, 249), "storage": ["N/A"]},
        {"name": "AirPods Max", "price": (549, 549), "storage": ["N/A"]}
    ],
    "Samsung": [
        {"name": "Galaxy S24 Ultra", "price": (1299, 1419), "storage": ["256GB", "512GB", "1TB"]},
        {"name": "Galaxy S24+", "price": (999, 1119), "storage": ["256GB", "512GB"]},
        {"name": "Galaxy Z Fold5", "price": (1799, 1919), "storage": ["256GB", "512GB", "1TB"]},
        {"name": "Galaxy Tab S9 Ultra", "price": (1199, 1319), "storage": ["256GB", "512GB"]},
        {"name": "Galaxy Watch6 Classic", "price": (399, 479), "storage": ["16GB"]},
        {"name": "Galaxy Buds2 Pro", "price": (229, 229), "storage": ["N/A"]}
    ],
    "Sony": [
        {"name": "WH-1000XM5 Headphones", "price": (348, 399), "storage": ["N/A"]},
        {"name": "WF-1000XM5 Earbuds", "price": (299, 299), "storage": ["N/A"]},
        {"name": "Xperia 1 V", "price": (1199, 1399), "storage": ["256GB", "512GB"]},
        {"name": "PlayStation 5 Slim", "price": (499, 499), "storage": ["1TB"]}
    ],
    "Dell": [
        {"name": "XPS 13 Plus", "price": (1199, 1499), "storage": ["512GB", "1TB"]},
        {"name": "Alienware m16 R2", "price": (1899, 2499), "storage": ["1TB", "2TB"]}
    ]
}
clothing_brands = ["Nike", "Adidas", "Zara", "Uniqlo", "Levi's", "The North Face", "Gucci", "Balenciaga"]
clothing_items = [
    {"type": "Tech Fleece Hoodie", "price": (110, 140), "is_shoe": False},
    {"type": "Air Max Sneakers", "price": (120, 180), "is_shoe": True},
    {"type": "Premium Cotton T-Shirt", "price": (25, 45), "is_shoe": False},
    {"type": "Slim Fit Jeans", "price": (60, 120), "is_shoe": False},
    {"type": "Puffer Jacket", "price": (150, 350), "is_shoe": False},
    {"type": "Running Shoes", "price": (80, 150), "is_shoe": True}
]
colors_tech = ["Titanium Black", "Natural Titanium", "Silver", "Space Grey", "Midnight", "Violet"]
colors_cloth = ["Black", "White", "Navy", "Grey", "Beige", "Red", "Olive"]
sizes_clothes = ["XS", "S", "M", "L", "XL", "XXL"]
sizes_shoes = ["39", "40", "41", "42", "43", "44", "45"]
materials_clothes = ["100% Cotton", "Polyester Blend", "Denim", "Wool", "Gore-Tex"]
materials_shoes = ["Leather", "Synthetic Mesh", "Suede", "Rubber", "Canvas"]
print("Generating 50 Products...")
for i in range(1, 51):
    cat = "Electronics" if random.random() > 0.5 else "Clothing"
    product_data = {}
    attrs = {}
    is_complete = random.random() > 0.15 
    if cat == "Electronics":
        brand = random.choice(list(electronics_db.keys()))
        model = random.choice(electronics_db[brand])
        name = model["name"]
        price = random.randint(model["price"][0], model["price"][1])
        if is_complete:
            if brand == "Apple": warranty = random.choice(["1 Year Limited", "AppleCare+"])
            elif brand == "Samsung": warranty = random.choice(["1 Year Standard", "Samsung Care+"])
            else: warranty = random.choice(["1 Year", "2 Years Manufacturer"])
            storage_val = random.choice(model["storage"])
            attrs = {
                "brand": brand,
                "color": random.choice(colors_tech),
                "storage": storage_val,
                "warranty": warranty
            }
            if not storage_val: attrs["storage"] = "N/A"
    else:
        brand = random.choice(clothing_brands)
        item = random.choice(clothing_items)
        name = f"{brand} {item['type']}"
        price = random.randint(item['price'][0], item['price'][1])
        if brand in ["Gucci", "Balenciaga"]: price = price * 5
        if is_complete:
            if item["is_shoe"]:
                size_val = random.choice(sizes_shoes)
                mat_val = random.choice(materials_shoes)
            else:
                size_val = random.choice(sizes_clothes)
                mat_val = random.choice(materials_clothes)
            attrs = {
                "brand": brand,
                "color": random.choice(colors_cloth),
                "size": size_val,
                "material": mat_val
            }
    status = "DRAFT"
    if is_complete:
        status = random.choice(["DRAFT", "PUBLISHED"])
    else:
        if random.random() > 0.8: name = "" 
    product = {
        "sku": f"SKU-{1000+i}",
        "name": name,
        "category": cat,
        "status": status,
        "price": float(price),
        "attributes": attrs
    }
    collection.insert_one(product)
    audit.insert_one({
        "sku": product["sku"],
        "action": "IMPORT_AUTO",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
print("50 Products inserted.")