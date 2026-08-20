import streamlit as st
import pandas as pd

def render_sidebar_filters(datasets: dict) -> dict:
    """
    Renders standard sidebar filters for Project Foresight and returns
    a dictionary of filtered datasets.
    """
    st.sidebar.markdown("## 🔍 Intelligence Filters")
    st.sidebar.markdown("---")
    
    df_sku = datasets.get("sku", pd.DataFrame())
    df_store = datasets.get("store", pd.DataFrame())
    df_flags = datasets.get("sku_flags", pd.DataFrame())
    df_cust = datasets.get("customer", pd.DataFrame())
    df_inv = datasets.get("inventory", pd.DataFrame())
    df_promo = datasets.get("promotions", pd.DataFrame())
    
    selected_categories = []
    selected_subcategories = []
    selected_brands = []
    selected_stores = []
    selected_store_types = []
    selected_cities = []
    selected_flags = []
    selected_loyalty = []
    
    # 1. Category Filter
    if not df_sku.empty and "category" in df_sku.columns:
        cats = sorted(df_sku["category"].dropna().unique())
        selected_categories = st.sidebar.multiselect("Select Category", options=cats, default=[])
    
    # 2. Subcategory Filter (cascaded if category selected)
    if not df_sku.empty and "subcategory" in df_sku.columns:
        if selected_categories:
            subcats_df = df_sku[df_sku["category"].isin(selected_categories)]
            subcats = sorted(subcats_df["subcategory"].dropna().unique())
        else:
            subcats = sorted(df_sku["subcategory"].dropna().unique())
        selected_subcategories = st.sidebar.multiselect("Select Subcategory", options=subcats, default=[])
        
    # 3. Brand Filter
    if not df_sku.empty and "brand" in df_sku.columns:
        brands = sorted(df_sku["brand"].dropna().unique())
        selected_brands = st.sidebar.multiselect("Select Brand", options=brands, default=[])

    # 4. Store Filter
    if not df_store.empty and "store_id" in df_store.columns:
        store_opts = sorted(df_store["store_id"].dropna().unique())
        selected_stores = st.sidebar.multiselect("Select Store ID", options=store_opts, default=[])
        
    # 5. Store Type Filter
    if not df_store.empty and "store_type" in df_store.columns:
        st_types = sorted(df_store["store_type"].dropna().unique())
        selected_store_types = st.sidebar.multiselect("Select Store Type", options=st_types, default=[])

    # 6. City Filter (combines Store & Customer cities if available)
    cities = set()
    if not df_store.empty and "city" in df_store.columns:
        cities.update(df_store["city"].dropna().unique())
    if not df_cust.empty and "city" in df_cust.columns:
        cities.update(df_cust["city"].dropna().unique())
    if cities:
        selected_cities = st.sidebar.multiselect("Select City", options=sorted(list(cities)), default=[])

    # 7. Stockout Risk Flag Filter
    if not df_flags.empty and "flag" in df_flags.columns:
        flags = sorted(df_flags["flag"].dropna().unique())
        selected_flags = st.sidebar.multiselect("Select Risk Flag", options=flags, default=[])

    # 8. Loyalty Segment Filter
    if not df_cust.empty and "loyalty_segment" in df_cust.columns:
        loyalty = sorted(df_cust["loyalty_segment"].dropna().unique())
        selected_loyalty = st.sidebar.multiselect("Select Loyalty Segment", options=loyalty, default=[])
        
    # Filter datasets based on active selections
    filtered_sku = df_sku.copy()
    if selected_categories:
        filtered_sku = filtered_sku[filtered_sku["category"].isin(selected_categories)]
    if selected_subcategories:
        filtered_sku = filtered_sku[filtered_sku["subcategory"].isin(selected_subcategories)]
    if selected_brands:
        filtered_sku = filtered_sku[filtered_sku["brand"].isin(selected_brands)]
        
    valid_sku_ids = set(filtered_sku["sku_id"].unique()) if not filtered_sku.empty else set()

    filtered_store = df_store.copy()
    if selected_stores:
        filtered_store = filtered_store[filtered_store["store_id"].isin(selected_stores)]
    if selected_store_types:
        filtered_store = filtered_store[filtered_store["store_type"].isin(selected_store_types)]
    if selected_cities and "city" in filtered_store.columns:
        filtered_store = filtered_store[filtered_store["city"].isin(selected_cities)]
        
    valid_store_ids = set(filtered_store["store_id"].unique()) if not filtered_store.empty else set()

    filtered_flags = df_flags.copy()
    if selected_flags:
        filtered_flags = filtered_flags[filtered_flags["flag"].isin(selected_flags)]
    if valid_sku_ids:
        filtered_flags = filtered_flags[filtered_flags["sku_id"].isin(valid_sku_ids)]

    filtered_inv = df_inv.copy()
    if valid_sku_ids:
        filtered_inv = filtered_inv[filtered_inv["sku_id"].isin(valid_sku_ids)]
    if valid_store_ids:
        filtered_inv = filtered_inv[filtered_inv["store_id"].isin(valid_store_ids)]
        
    filtered_cust = df_cust.copy()
    if selected_cities and "city" in filtered_cust.columns:
        filtered_cust = filtered_cust[filtered_cust["city"].isin(selected_cities)]
    if selected_loyalty:
        filtered_cust = filtered_cust[filtered_cust["loyalty_segment"].isin(selected_loyalty)]

    return {
        "sku": filtered_sku,
        "store": filtered_store,
        "inventory": filtered_inv,
        "sku_flags": filtered_flags,
        "customer": filtered_cust,
        "promotions": df_promo,
        "active_filters": {
            "categories": selected_categories,
            "subcategories": selected_subcategories,
            "brands": selected_brands,
            "stores": selected_stores,
            "store_types": selected_store_types,
            "cities": selected_cities,
            "flags": selected_flags,
            "loyalty": selected_loyalty
        }
    }
