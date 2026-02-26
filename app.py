import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
st.set_page_config(page_title="Multi-channel product catalog", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #0E1117; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { background-color: #262730; border-bottom: 2px solid #FF4B4B; }
    div[data-testid="stExpander"] { background-color: #262730; border: none; border-radius: 8px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)
try:
    client = MongoClient('mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000')
    client.admin.command('ping')
    db = client['Multi-channel product catalog']
    collection = db['products']
    audit_collection = db['audit']
except:
    st.error("MongoDB Connection Error")
    st.stop()
def check_quality(product):
    errors = []
    if not product.get('name'): errors.append("Name required")
    if not product.get('sku'): errors.append("SKU required")
    if product.get('price', 0) <= 0: errors.append("Price invalid")
    cat = product.get('category')
    attrs = product.get('attributes', {})
    if cat == 'Clothing':
        if not attrs.get('brand'): errors.append("Brand required")
        if not attrs.get('color'): errors.append("Color required")
        if not attrs.get('size'): errors.append("Size required")
        if not attrs.get('material'): errors.append("Material required")
    elif cat == 'Electronics':
        if not attrs.get('brand'): errors.append("Brand required")
        if not attrs.get('color'): errors.append("Color required")
        if not attrs.get('storage'): errors.append("Storage required")
        if not attrs.get('warranty'): errors.append("Warranty required")
    return len(errors) == 0, errors
def log_audit(sku, action):
    audit_collection.insert_one({
        "sku": sku, "action": action, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
st.title("Catalogue produits multi-canaux")
tab_cat, tab_add, tab_exp, tab_log = st.tabs(["CATALOG", "ADD NEW", "CHANNELS & EXPORT", "LOGS"])
with tab_cat:
    c1, c2 = st.columns([3, 1])
    search_term = c1.text_input("Search Product", placeholder="Type name, brand...", key="search_main")
    cat_filter = c2.selectbox("Filter by Category", ["All", "Clothing", "Electronics"], key="cat_filter_main")
    query = {}
    if cat_filter != "All":
        query["category"] = cat_filter
    if search_term:
        query["$text"] = {"$search": search_term}
    try:
        products = list(collection.find(query))
    except Exception as e:
        st.error(f"Erreur de recherche : {e}")
        products = []
    st.markdown(f"**{len(products)} Items found**")
    st.markdown("---")
    for prod in products:
        is_valid, errors = check_quality(prod)
        status = "[LIVE]" if prod.get('status') == 'PUBLISHED' else "[DRAFT]"
        card_title = f"{status} {prod.get('name', 'No Name')} | {prod.get('sku', 'No SKU')} | ${prod.get('price', 0)}"
        with st.expander(card_title):
            c_a, c_b = st.columns(2)
            with c_a:
                st.caption("GENERAL INFO")
                new_price = st.number_input("Price ($)", value=float(prod.get('price', 0)), key=f"p_{prod['_id']}")
                st.info(f"Category: {prod.get('category')}")
                if not is_valid:
                    st.error(f"Missing: {', '.join(errors)}")
            with c_b:
                st.caption("ATTRIBUTES (Variant Data)")
                attrs = prod.get('attributes', {})
                if prod.get('category') == 'Clothing':
                    r1_x, r1_y = st.columns(2)
                    attrs['brand'] = r1_x.text_input("Brand", attrs.get('brand',''), key=f"b_{prod['_id']}")
                    attrs['color'] = r1_y.text_input("Color", attrs.get('color',''), key=f"c_{prod['_id']}")
                    r2_x, r2_y = st.columns(2)
                    attrs['size'] = r2_x.text_input("Size", attrs.get('size',''), key=f"s_{prod['_id']}")
                    attrs['material'] = r2_y.text_input("Material", attrs.get('material',''), key=f"m_{prod['_id']}")
                elif prod.get('category') == 'Electronics':
                    r1_x, r1_y = st.columns(2)
                    attrs['brand'] = r1_x.text_input("Brand", attrs.get('brand',''), key=f"b_{prod['_id']}")
                    attrs['color'] = r1_y.text_input("Finish", attrs.get('color',''), key=f"c_{prod['_id']}")
                    r2_x, r2_y = st.columns(2)
                    attrs['storage'] = r2_x.text_input("Storage", attrs.get('storage',''), key=f"st_{prod['_id']}")
                    attrs['warranty'] = r2_y.text_input("Warranty", attrs.get('warranty',''), key=f"w_{prod['_id']}")
            st.markdown("<br>", unsafe_allow_html=True)
            col_save, col_pub = st.columns([1, 4])
            if col_save.button("SAVE", key=f"save_{prod['_id']}", use_container_width=True):
                collection.update_one({'_id': prod['_id']}, {"$set": {"price": new_price, "attributes": attrs}})
                log_audit(prod.get('sku'), "UPDATE")
                st.rerun()
            if is_valid and prod.get('status') != 'PUBLISHED':
                if col_pub.button("PUBLISH TO CHANNELS", key=f"pub_{prod['_id']}", type="primary", use_container_width=True):
                    collection.update_one({'_id': prod['_id']}, {"$set": {"status": "PUBLISHED"}})
                    log_audit(prod.get('sku'), "PUBLISH")
                    st.rerun()
with tab_add:
    st.subheader("Create New Product")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        sku = c1.text_input("SKU Reference", value=f"SKU-{collection.count_documents({})+1000}", key="new_sku")
        name = c2.text_input("Product Name", key="new_name")
        cat = st.selectbox("Category", ["Clothing", "Electronics"], key="new_cat")
        if st.button("CREATE DRAFT", type="primary", key="btn_create"):
            if sku and name:
                try:
                    collection.insert_one({
                        "sku": sku, "name": name, "category": cat, 
                        "status": "DRAFT", "price": 0, "attributes": {}
                    })
                    log_audit(sku, "CREATE")
                    st.success("Product created! Go to Catalog to add details.")
                except:
                    st.error(f"Error: SKU '{sku}' already exists.")
with tab_exp:
    st.header("Multi-Channel Distribution")
    st.markdown("Select a sales channel to generate the appropriate data feed.")
    channel = st.selectbox("Destination Channel", 
                           ["E-Commerce Website (JSON)", "Marketplace (CSV)", "Social Media (CSV)"],
                           key="export_channel")
    st.info(f"Generating feed for: **{channel}**")
    if st.button("GENERATE FEED", type="primary"):
        data = list(collection.find({"status": "PUBLISHED"}, {"_id": 0}))
        if data:
            if "JSON" in channel:
                json_data = pd.DataFrame(data).to_json(orient='records')
                st.download_button("Download JSON Feed", json_data, "website_feed.json", "application/json")
                st.success("JSON Feed ready for Web integration.")
            elif "Marketplace" in channel:
                df = pd.json_normalize(data)
                df.columns = df.columns.str.replace("attributes.", "", regex=False).str.capitalize()
                core_cols = ['Sku', 'Name', 'Category', 'Price', 'Status']
                first_cols = [c for c in core_cols if c in df.columns]
                other_cols = [c for c in df.columns if c not in first_cols]
                df = df[first_cols + other_cols]
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV Feed", csv, "marketplace_feed.csv", "text/csv")
                st.success("CSV Feed ready for Marketplace .")     
            else:
                df = pd.json_normalize(data)
                cols = ['sku', 'name', 'price', 'category']
                existing_cols = [c for c in cols if c in df.columns]
                csv = df[existing_cols].to_csv(index=False).encode('utf-8')
                st.download_button("Download Catalog", csv, "social_feed.csv", "text/csv")
                st.success("Social Catalog ready.")
        else:
            st.warning("No published products found. Please publish items first.")
with tab_log:
    st.subheader("Audit Log & Traceability")
    filter_query = {
        "action": {"$in": ["CREATE", "UPDATE", "PUBLISH"]},
        "sku": {"$ne": None}
    }
    logs = list(audit_collection.find(filter_query, {"_id": 0}).limit(50))
    if logs:
        df_log = pd.DataFrame(logs)
        if 'timestamp' in df_log.columns:
            df_log['timestamp'] = pd.to_datetime(df_log['timestamp'], errors='coerce')
            df_log = df_log.sort_values(by='timestamp', ascending=False)
        st.dataframe(df_log, use_container_width=True, hide_index=True)
    else:
        st.info("No manual activity recorded yet.")