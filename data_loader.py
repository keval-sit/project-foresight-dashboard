import os
import pandas as pd
import streamlit as st

# Expected columns dictionary for validation
EXPECTED_COLUMNS = {
    "customer_clean.csv": [
        "cust_id", "age", "gender", "city", "loyalty_segment", "preferred_channel", "registration_date"
    ],
    "inventory_clean.csv": [
        "store_id", "sku_id", "stock_on_hand", "reorder_point", "safety_stock", "last_restock_date"
    ],
    "promotions_clean.csv": [
        "promo_id", "promo_name", "start_date", "end_date", "discount_pct", "promo_type", "target_type", "target_value"
    ],
    "sku_clean.csv": [
        "sku_id", "sku_name", "category", "subcategory", "unit_price", "cost_price", "brand"
    ],
    "sku_flags_clean.csv": [
        "sku_id", "flag", "affected_stores", "window_start", "window_end", "notes"
    ],
    "store_clean.csv": [
        "store_id", "store_name", "city", "store_type", "opening_date"
    ]
}

@st.cache_data
def load_csv_file(file_path: str, filename: str) -> pd.DataFrame:
    """Helper function to load an individual CSV file with error validation."""
    if not os.path.exists(file_path):
        st.error(f"Missing required data file: `{filename}` at path: `{file_path}`")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            st.warning(f"File `{filename}` is empty.")
            return df
        
        # Verify required columns
        expected_cols = EXPECTED_COLUMNS.get(filename, [])
        missing_cols = [col for col in expected_cols if col not in df.columns]
        if missing_cols:
            st.error(f"File `{filename}` is missing mandatory columns: {missing_cols}")
            
        return df
    except Exception as e:
        st.error(f"Error loading CSV file `{filename}`: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_all_datasets(data_dir: str):
    """Loads all 6 cleaned datasets required for Project Foresight."""
    customer_path = os.path.join(data_dir, "customer_clean.csv")
    inventory_path = os.path.join(data_dir, "inventory_clean.csv")
    promotions_path = os.path.join(data_dir, "promotions_clean.csv")
    sku_path = os.path.join(data_dir, "sku_clean.csv")
    sku_flags_path = os.path.join(data_dir, "sku_flags_clean.csv")
    store_path = os.path.join(data_dir, "store_clean.csv")

    df_customer = load_csv_file(customer_path, "customer_clean.csv")
    df_inventory = load_csv_file(inventory_path, "inventory_clean.csv")
    df_promotions = load_csv_file(promotions_path, "promotions_clean.csv")
    df_sku = load_csv_file(sku_path, "sku_clean.csv")
    df_sku_flags = load_csv_file(sku_flags_path, "sku_flags_clean.csv")
    df_store = load_csv_file(store_path, "store_clean.csv")

    return {
        "customer": df_customer,
        "inventory": df_inventory,
        "promotions": df_promotions,
        "sku": df_sku,
        "sku_flags": df_sku_flags,
        "store": df_store
    }
