import pandas as pd
import numpy as np

def classify_inventory_status(stock_on_hand: float, reorder_point: float, safety_stock: float) -> str:
    """
    Classifies inventory status based on CURRENT INVENTORY RULE-BASED STATUS.
    Note: This is a rule-based inventory check, not a forecasting model.
    """
    if pd.isna(stock_on_hand):
        return "Unknown"
    
    if stock_on_hand < safety_stock:
        return "Critical"
    elif stock_on_hand < reorder_point:
        return "Reorder"
    else:
        return "Healthy"

def compute_inventory_summary(df_inv: pd.DataFrame, df_sku: pd.DataFrame, df_flags: pd.DataFrame, df_store: pd.DataFrame):
    """Calculates executive KPI metrics strictly from available dataset tables."""
    if df_inv.empty or df_sku.empty:
        return {
            "total_skus": 0, "total_stores": 0, "total_units": 0,
            "avg_stock_per_sku": 0, "stockout_risk_skus": 0,
            "flagged_skus": 0, "avg_unit_price": 0.0, "total_inventory_cost": 0.0
        }
    
    # Merge inventory with SKU details
    df_merged = pd.merge(df_inv, df_sku, on="sku_id", how="inner")
    
    total_skus = df_sku["sku_id"].nunique()
    total_stores = df_store["store_id"].nunique() if not df_store.empty else df_inv["store_id"].nunique()
    total_units = df_merged["stock_on_hand"].sum()
    avg_stock_per_sku = total_units / total_skus if total_skus > 0 else 0.0
    
    # Calculate stockout risk SKUs (Critical status or STOCKOUT_RISK flag)
    df_merged["inventory_status"] = df_merged.apply(
        lambda r: classify_inventory_status(r["stock_on_hand"], r["reorder_point"], r["safety_stock"]), axis=1
    )
    
    critical_skus = set(df_merged[df_merged["inventory_status"] == "Critical"]["sku_id"].unique())
    stockout_flag_skus = set(df_flags[df_flags["flag"] == "STOCKOUT_RISK"]["sku_id"].unique()) if not df_flags.empty else set()
    all_stockout_risk_skus = critical_skus.union(stockout_flag_skus)
    
    flagged_skus_count = df_flags["sku_id"].nunique() if not df_flags.empty else 0
    avg_unit_price = df_sku["unit_price"].mean() if not df_sku.empty else 0.0
    
    df_merged["inventory_cost"] = df_merged["stock_on_hand"] * df_merged["cost_price"]
    total_inventory_cost = df_merged["inventory_cost"].sum()
    
    return {
        "total_skus": total_skus,
        "total_stores": total_stores,
        "total_units": float(total_units),
        "avg_stock_per_sku": float(avg_stock_per_sku),
        "stockout_risk_skus": len(all_stockout_risk_skus),
        "flagged_skus": flagged_skus_count,
        "avg_unit_price": float(avg_unit_price),
        "total_inventory_cost": float(total_inventory_cost),
        "df_merged": df_merged
    }

def compute_product_margins(df_sku: pd.DataFrame) -> pd.DataFrame:
    """Calculates Gross Margin and Gross Margin % per unit."""
    if df_sku.empty:
        return df_sku
    
    df = df_sku.copy()
    df["gross_margin"] = df["unit_price"] - df["cost_price"]
    df["gross_margin_pct"] = np.where(
        df["unit_price"] > 0,
        (df["gross_margin"] / df["unit_price"]) * 100,
        0.0
    )
    return df
