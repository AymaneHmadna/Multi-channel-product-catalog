from pymongo import MongoClient, TEXT, ASCENDING
try:
    client = MongoClient('mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000')
    client.admin.command('ping')
    db = client['Catalogue_produits_multi_canaux']
    products = db['products']
    audit = db['audit']
    print("Connexion réussie.")
except Exception as e:
    print(f"Erreur de connexion : {e}")
    exit()
print("Nettoyage des anciens index...")
try:
    products.drop_indexes()
    audit.drop_indexes()
except:
    pass
print("Configuration des index Produits...")
products.create_index("sku", unique=True)
print("  - Index Unique (SKU) : OK")
products.create_index([("name", TEXT), ("attributes.brand", TEXT)])
print("  - Index Textuel (Recherche) : OK")
products.create_index("category")
products.create_index("status")
products.create_index("price")
print("  - Index Filtres (Catégorie/Statut/Prix) : OK")
products.create_index("attributes.brand")
products.create_index("attributes.color")
products.create_index("attributes.size")
products.create_index("attributes.material")
products.create_index("attributes.storage")
print("  - Index Attributs (Size/Material/Storage...) : OK")
print("Configuration des index Audit...")
audit.create_index([("timestamp", ASCENDING)])
print("  - Index Chronologique (Audit) : OK")
print("\nTERMINÉ ! Base de données optimisée.")