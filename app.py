import os
import pandas as pd
import numpy as np
import streamlit as st

from utils.data_loader import load_all_datasets
from utils.filters import render_sidebar_filters
from utils.metrics import classify_inventory_status, compute_inventory_summary, compute_product_margins
from utils.charts import (
    create_bar_chart, create_pie_chart, create_stock_vs_reorder_chart, create_promo_timeline,
    COLOR_CRITICAL, COLOR_REORDER, COLOR_HEALTHY, ACCENT_BLUE, ACCENT_CYAN
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & CUSTOM CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PROJECT FORESIGHT – Demand & Inventory Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    /* Dark Theme Core Styles */
    .stApp {
        background-color: #0e1117;
        color: #e0e6ed;
    }
    sidebar .sidebar-content {
        background-color: #131722;
    }
    
    /* Header Container */
    .main-header {
        background: linear-gradient(135deg, #1e2638 0%, #0e1117 100%);
        padding: 24px 30px;
        border-radius: 12px;
        border: 1px solid #2a3447;
        margin-bottom: 25px;
    }
    .main-header h1 {
        color: #00f2fe;
        font-family: 'Inter', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    
    /* KPI Card Styles */
    .kpi-card {
        background-color: #131722;
        border: 1px solid #2a3447;
        border-radius: 10px;
        padding: 18px 20px;
        text-align: left;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        border-color: #4facfe;
        transform: translateY(-2px);
    }
    .kpi-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .kpi-value {
        color: #ffffff;
        font-size: 1.7rem;
        font-weight: 700;
        margin: 0;
    }
    .kpi-sub {
        color: #00f2fe;
        font-size: 0.8rem;
        margin-top: 4px;
    }

    /* Badges */
    .badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-critical { background-color: rgba(255, 82, 82, 0.2); color: #ff5252; border: 1px solid #ff5252; }
    .badge-reorder { background-color: rgba(255, 159, 67, 0.2); color: #ff9f43; border: 1px solid #ff9f43; }
    .badge-healthy { background-color: rgba(0, 184, 148, 0.2); color: #00b894; border: 1px solid #00b894; }
    .badge-stockout { background-color: rgba(235, 77, 75, 0.25); color: #ff7979; border: 1px solid #ff7979; }
    .badge-pending { background-color: rgba(241, 196, 15, 0.2); color: #f1c40f; border: 1px solid #f1c40f; }
    .badge-completed { background-color: rgba(46, 204, 113, 0.2); color: #2ecc71; border: 1px solid #2ecc71; }

    /* Pending Notice Box */
    .pending-box {
        background: rgba(241, 196, 15, 0.08);
        border: 1px solid #f1c40f;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 25px;
        color: #f39c12;
        font-weight: 500;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA LOADING & FILTERING
# -----------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
raw_datasets = load_all_datasets(DATA_DIR)
filtered_datasets = render_sidebar_filters(raw_datasets)

df_sku = filtered_datasets["sku"]
df_store = filtered_datasets["store"]
df_inv = filtered_datasets["inventory"]
df_flags = filtered_datasets["sku_flags"]
df_cust = filtered_datasets["customer"]
df_promo = filtered_datasets["promotions"]

# -----------------------------------------------------------------------------
# NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.markdown("---")
pages = [
    "1. Executive Overview",
    "2. Inventory Analysis",
    "3. Risk Dashboard",
    "4. SKU Explorer",
    "5. Store Analysis",
    "6. Product Analysis",
    "7. Promotion Analysis",
    "8. Forecast (Pending)",
    "9. Recommendations (Pending)",
    "10. Methodology"
]

selected_page = st.sidebar.radio("📌 Navigation Menu", pages)

# Header Display
st.markdown(f"""
<div class="main-header">
    <h1>PROJECT FORESIGHT – Demand & Inventory Intelligence</h1>
    <p>Decision-Support Dashboard | Stage: Data Cleaning Completed | Active View: {selected_page}</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# -----------------------------------------------------------------------------
if selected_page == "1. Executive Overview":
    summary = compute_inventory_summary(df_inv, df_sku, df_flags, df_store)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Catalog SKUs</div>
            <div class="kpi-value">{summary['total_skus']:,}</div>
            <div class="kpi-sub">Filtered assortment</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Active Store Count</div>
            <div class="kpi-value">{summary['total_stores']:,}</div>
            <div class="kpi-sub">Network locations</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Inventory Units</div>
            <div class="kpi-value">{int(summary['total_units']):,}</div>
            <div class="kpi-sub">SUM(stock_on_hand)</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Stock per SKU</div>
            <div class="kpi-value">{summary['avg_stock_per_sku']:.1f}</div>
            <div class="kpi-sub">Units / SKU</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">SKUs at Stockout Risk</div>
            <div class="kpi-value" style="color: #ff5252;">{summary['stockout_risk_skus']:,}</div>
            <div class="kpi-sub">Critical / Depleted stock</div>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Flagged Risk SKUs</div>
            <div class="kpi-value" style="color: #ff9f43;">{summary['flagged_skus']:,}</div>
            <div class="kpi-sub">sku_flags_clean records</div>
        </div>
        """, unsafe_allow_html=True)
    with col7:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Unit Price</div>
            <div class="kpi-value">PKR {summary['avg_unit_price']:.2f}</div>
            <div class="kpi-sub">Mean selling price</div>
        </div>
        """, unsafe_allow_html=True)
    with col8:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Inventory Cost</div>
            <div class="kpi-value">PKR {summary['total_inventory_cost']:,.0f}</div>
            <div class="kpi-sub">SUM(stock × cost_price)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>### 📊 Portfolio Executive Analytics", unsafe_allow_html=True)
    df_merged = summary.get("df_merged", pd.DataFrame())
    
    if not df_merged.empty:
        c1, c2 = st.columns(2)
        with c1:
            cat_inv = df_merged.groupby("category")["stock_on_hand"].sum().reset_index()
            fig1 = create_bar_chart(cat_inv, x="category", y="stock_on_hand", title="Inventory Units by Category")
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            store_inv = df_merged.groupby("store_id")["stock_on_hand"].sum().reset_index()
            fig2 = create_bar_chart(store_inv, x="store_id", y="stock_on_hand", title="Inventory Units by Store")
            st.plotly_chart(fig2, use_container_width=True)
            
        c3, c4 = st.columns(2)
        with c3:
            status_dist = df_merged["inventory_status"].value_counts().reset_index()
            status_dist.columns = ["Status", "Count"]
            color_map = {"Critical": COLOR_CRITICAL, "Reorder": COLOR_REORDER, "Healthy": COLOR_HEALTHY}
            fig3 = create_pie_chart(status_dist, names="Status", values="Count", title="Stockout Risk Status Distribution", color_map=color_map)
            st.plotly_chart(fig3, use_container_width=True)
        with c4:
            cat_cost = df_merged.groupby("category")["inventory_cost"].sum().reset_index()
            fig4 = create_bar_chart(cat_cost, x="category", y="inventory_cost", title="Total Inventory Cost by Category (PKR)")
            st.plotly_chart(fig4, use_container_width=True)

        st.markdown("#### 🏆 Top 10 SKUs by Inventory Value")
        top_val_skus = df_merged.groupby(["sku_id", "sku_name", "category"])["inventory_cost"].sum().reset_index().sort_values("inventory_cost", ascending=False).head(10)
        fig5 = create_bar_chart(top_val_skus, x="inventory_cost", y="sku_name", title="Top 10 SKUs by Total Inventory Value", orientation="h")
        st.plotly_chart(fig5, use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 2: INVENTORY ANALYSIS
# -----------------------------------------------------------------------------
elif selected_page == "2. Inventory Analysis":
    st.info("ℹ️ **CURRENT INVENTORY RULE-BASED STATUS**: Inventory status is derived strictly via rule logic (`stock_on_hand` vs `safety_stock` and `reorder_point`). It is NOT a predictive ML model.")

    df_merged = pd.merge(df_inv, df_sku, on="sku_id", how="inner") if not df_inv.empty and not df_sku.empty else pd.DataFrame()
    
    if not df_merged.empty:
        df_merged["inventory_status"] = df_merged.apply(
            lambda r: classify_inventory_status(r["stock_on_hand"], r["reorder_point"], r["safety_stock"]), axis=1
        )
        df_merged["inventory_value"] = df_merged["stock_on_hand"] * df_merged["cost_price"]

        s_hand = df_merged["stock_on_hand"].sum()
        r_point = df_merged["reorder_point"].sum()
        s_stock = df_merged["safety_stock"].sum()
        above_reorder = df_merged[df_merged["stock_on_hand"] >= df_merged["reorder_point"]]["stock_on_hand"].sum()
        below_reorder = df_merged[df_merged["stock_on_hand"] < df_merged["reorder_point"]]["stock_on_hand"].sum()
        total_val = df_merged["inventory_value"].sum()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Stock on Hand", f"{int(s_hand):,}")
        m2.metric("Reorder Point Baseline", f"{int(r_point):,}")
        m3.metric("Safety Stock Target", f"{int(s_stock):,}")
        m4.metric("Total Inventory Value", f"PKR {total_val:,.0f}")

        m5, m6 = st.columns(2)
        m5.metric("Stock Above Reorder Point", f"{int(above_reorder):,} units")
        m6.metric("Stock Below Reorder Point", f"{int(below_reorder):,} units")

        st.markdown("<br>### 📉 Inventory Comparison & Distribution", unsafe_allow_html=True)
        st.plotly_chart(create_stock_vs_reorder_chart(df_merged), use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### ⬆️ Top 10 SKUs by Stock Quantity")
            top_qty = df_merged.groupby("sku_name")["stock_on_hand"].sum().reset_index().sort_values("stock_on_hand", ascending=False).head(10)
            st.plotly_chart(create_bar_chart(top_qty, x="stock_on_hand", y="sku_name", title="Highest Stock SKUs", orientation="h"), use_container_width=True)
        with c2:
            st.markdown("#### ⬇️ Lowest-Stock SKUs (Need Restock)")
            low_qty = df_merged.groupby("sku_name")["stock_on_hand"].sum().reset_index().sort_values("stock_on_hand", ascending=True).head(10)
            st.plotly_chart(create_bar_chart(low_qty, x="stock_on_hand", y="sku_name", title="Lowest Stock SKUs", orientation="h"), use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 3: RISK DASHBOARD
# -----------------------------------------------------------------------------
elif selected_page == "3. Risk Dashboard":
    st.markdown("### ⚠️ Inventory Risk & Flag Intelligence")
    
    if df_flags.empty:
        st.warning("No SKU risk flags match the selected filters.")
    else:
        df_risk_merged = pd.merge(df_flags, df_sku, on="sku_id", how="inner")
        
        # Parse affected stores count
        def get_affected_count(stores_str):
            if pd.isna(stores_str):
                return 0
            return len([s.strip() for s in str(stores_str).split(",") if s.strip()])
            
        df_risk_merged["affected_store_count"] = df_risk_merged["affected_stores"].apply(get_affected_count)
        
        stockout_count = len(df_risk_merged[df_risk_merged["flag"] == "STOCKOUT_RISK"])
        slow_mover_count = len(df_risk_merged[df_risk_merged["flag"] == "SLOW_MOVER"])
        total_affected_stores = df_risk_merged["affected_store_count"].sum()

        r1, r2, r3 = st.columns(3)
        r1.metric("Stockout Risk SKUs", f"{stockout_count:,}")
        r2.metric("Slow Mover SKUs", f"{slow_mover_count:,}")
        r3.metric("Total Affected Store Instances", f"{total_affected_stores:,}")

        c1, c2 = st.columns(2)
        with c1:
            flag_dist = df_risk_merged["flag"].value_counts().reset_index()
            flag_dist.columns = ["Risk Flag", "Count"]
            st.plotly_chart(create_pie_chart(flag_dist, names="Risk Flag", values="Count", title="Risk Distribution by Flag"), use_container_width=True)
        with c2:
            risk_cat = df_risk_merged.groupby(["category", "flag"])["sku_id"].count().reset_index()
            st.plotly_chart(create_bar_chart(risk_cat, x="category", y="sku_id", color="flag", title="Risk SKUs by Category"), use_container_width=True)

        st.markdown("#### 📋 Prioritized SKU Risk Master Table")
        st.dataframe(
            df_risk_merged[["sku_id", "sku_name", "category", "brand", "flag", "affected_stores", "window_start", "window_end", "notes"]],
            use_container_width=True
        )

# -----------------------------------------------------------------------------
# PAGE 4: SKU EXPLORER
# -----------------------------------------------------------------------------
elif selected_page == "4. SKU Explorer":
    st.markdown("### 🔍 Interactive SKU Intelligence Explorer")
    
    if df_sku.empty:
        st.warning("No SKUs available under active filters.")
    else:
        sku_list = df_sku["sku_id"] + " - " + df_sku["sku_name"]
        selected_sku_str = st.selectbox("Select a Product SKU to Explore:", options=sku_list)
        selected_sku_id = selected_sku_str.split(" - ")[0]
        
        sku_info = df_sku[df_sku["sku_id"] == selected_sku_id].iloc[0]
        sku_inv = df_inv[df_inv["sku_id"] == selected_sku_id] if not df_inv.empty else pd.DataFrame()
        sku_flag = df_flags[df_flags["sku_id"] == selected_sku_id] if not df_flags.empty else pd.DataFrame()

        tot_stock = sku_inv["stock_on_hand"].sum() if not sku_inv.empty else 0.0
        reorder_p = sku_inv["reorder_point"].sum() if not sku_inv.empty else 0.0
        safety_s = sku_inv["safety_stock"].sum() if not sku_inv.empty else 0.0
        
        rule_status = classify_inventory_status(tot_stock, reorder_p, safety_s)
        has_flag = sku_flag["flag"].iloc[0] if not sku_flag.empty else "None"
        aff_stores = sku_flag["affected_stores"].iloc[0] if not sku_flag.empty else "N/A"
        flag_notes = sku_flag["notes"].iloc[0] if not sku_flag.empty else "No current risk flags recorded."

        e1, e2, e3, e4 = st.columns(4)
        e1.metric("SKU ID", sku_info['sku_id'])
        e2.metric("Category", sku_info['category'])
        e3.metric("Brand", sku_info['brand'])
        e4.metric("Selling Price", f"PKR {sku_info['unit_price']:.2f}")

        e5, e6, e7, e8 = st.columns(4)
        e5.metric("Current Total Stock", f"{tot_stock:,.0f} units")
        e6.metric("Reorder Threshold", f"{reorder_p:,.0f}")
        e7.metric("Rule-Based Status", rule_status)
        e8.metric("Active Risk Flag", has_flag)

        st.markdown(f"**Risk Notes**: `{flag_notes}` | **Affected Stores**: `{aff_stores}`")

        st.markdown("#### 🏢 Store Level Inventory Allocation")
        if not sku_inv.empty and not df_store.empty:
            sku_inv_store = pd.merge(sku_inv, df_store, on="store_id", how="inner")
            st.plotly_chart(create_bar_chart(sku_inv_store, x="store_name", y="stock_on_hand", title=f"Stock Distribution for {sku_info['sku_name']}"), use_container_width=True)
            st.dataframe(sku_inv_store[["store_id", "store_name", "city", "store_type", "stock_on_hand", "reorder_point", "safety_stock"]], use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 5: STORE ANALYSIS
# -----------------------------------------------------------------------------
elif selected_page == "5. Store Analysis":
    st.markdown("### 🏪 Network Store Inventory Intelligence")
    
    if df_store.empty or df_inv.empty:
        st.warning("No store data available.")
    else:
        df_store_inv = pd.merge(df_inv, df_sku, on="sku_id", how="inner")
        df_store_inv["inv_cost"] = df_store_inv["stock_on_hand"] * df_store_inv["cost_price"]

        store_summary = df_store_inv.groupby("store_id").agg(
            total_skus=("sku_id", "nunique"),
            total_stock=("stock_on_hand", "sum"),
            total_cost=("inv_cost", "sum")
        ).reset_index()

        df_store_master = pd.merge(df_store, store_summary, on="store_id", how="left").fillna(0)

        s1, s2, s3 = st.columns(3)
        s1.metric("Total Stores", f"{len(df_store_master):,}")
        s2.metric("Total Stock Across Stores", f"{int(df_store_master['total_stock'].sum()):,} units")
        s3.metric("Total Store Capital", f"PKR {df_store_master['total_cost'].sum():,.0f}")

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(create_bar_chart(df_store_master, x="store_name", y="total_stock", title="Total Stock by Store"), use_container_width=True)
        with c2:
            st.plotly_chart(create_bar_chart(df_store_master, x="store_name", y="total_cost", title="Inventory Value by Store (PKR)"), use_container_width=True)

        st.markdown("#### 🏢 Store Master Summary Table")
        st.dataframe(df_store_master[["store_id", "store_name", "city", "store_type", "total_skus", "total_stock", "total_cost"]], use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 6: PRODUCT ANALYSIS
# -----------------------------------------------------------------------------
elif selected_page == "6. Product Analysis":
    st.markdown("### 🏷️ Product Catalog & Margin Intelligence")
    
    if df_sku.empty:
        st.warning("No product data available.")
    else:
        df_margin = compute_product_margins(df_sku)
        
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Total SKUs", f"{len(df_margin):,}")
        p2.metric("Avg Unit Price", f"PKR {df_margin['unit_price'].mean():.2f}")
        p3.metric("Avg Unit Cost", f"PKR {df_margin['cost_price'].mean():.2f}")
        p4.metric("Avg Gross Margin %", f"{df_margin['gross_margin_pct'].mean():.1f}%")

        c1, c2 = st.columns(2)
        with c1:
            cat_count = df_margin["category"].value_counts().reset_index()
            cat_count.columns = ["Category", "Product Count"]
            st.plotly_chart(create_bar_chart(cat_count, x="Category", y="Product Count", title="Products by Category"), use_container_width=True)
        with c2:
            cat_margin = df_margin.groupby("category")["gross_margin_pct"].mean().reset_index()
            st.plotly_chart(create_bar_chart(cat_margin, x="category", y="gross_margin_pct", title="Average Gross Margin % by Category"), use_container_width=True)

        st.markdown("#### 📄 SKU Price & Margin Table")
        st.dataframe(df_margin[["sku_id", "sku_name", "category", "subcategory", "brand", "unit_price", "cost_price", "gross_margin", "gross_margin_pct"]], use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 7: PROMOTION ANALYSIS
# -----------------------------------------------------------------------------
elif selected_page == "7. Promotion Analysis":
    st.markdown("### 📢 Promotional Campaign Intelligence")
    
    st.warning("⚠️ **IMPORTANT**: Promotions are displayed based on promotional master records (`promotions_clean.csv`). Do NOT infer sales lift or promotional impact as historical demand transactions are pending.")

    if df_promo.empty:
        st.warning("No promotional campaign data available.")
    else:
        pr1, pr2, pr3 = st.columns(3)
        pr1.metric("Total Campaigns", f"{len(df_promo):,}")
        pr2.metric("Avg Discount %", f"{df_promo['discount_pct'].mean():.1f}%")
        pr3.metric("Target Types Count", f"{df_promo['target_type'].nunique():,}")

        c1, c2 = st.columns(2)
        with c1:
            ptype_dist = df_promo["promo_type"].value_counts().reset_index()
            ptype_dist.columns = ["Promotion Type", "Count"]
            st.plotly_chart(create_pie_chart(ptype_dist, names="Promotion Type", values="Count", title="Promotion Type Distribution"), use_container_width=True)
        with c2:
            ttype_dist = df_promo["target_type"].value_counts().reset_index()
            ttype_dist.columns = ["Target Type", "Count"]
            st.plotly_chart(create_pie_chart(ttype_dist, names="Target Type", values="Count", title="Target Type Distribution"), use_container_width=True)

        st.markdown("#### 📅 Promotions Timeline")
        st.plotly_chart(create_promo_timeline(df_promo), use_container_width=True)

        st.markdown("#### 📋 Campaign Details Table")
        st.dataframe(df_promo, use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 8: FORECAST (Pending Module UI)
# -----------------------------------------------------------------------------
elif selected_page == "8. Forecast (Pending)":
    st.markdown("""
    <div class="pending-box">
        <h4>⏳ Demand Forecasting Module Pending</h4>
        <p>Forecasting results will appear after the demand forecasting ML pipeline is trained and executed. The architecture below is ready to seamlessly bind <code>forecast_results.csv</code> once available.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔮 Future Demand Forecasting Architecture")
    
    selected_sku_fc = st.selectbox("Select SKU for Forecast Preview:", options=df_sku["sku_id"] + " - " + df_sku["sku_name"] if not df_sku.empty else ["N/A"])
    horizon = st.select_slider("Forecast Horizon (Days):", options=[7, 14, 28, 60, 90], value=28)

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("WAPE (Target Metric)", "Pending", help="Weighted Absolute Percentage Error")
    f2.metric("MAPE", "Pending", help="Mean Absolute Percentage Error")
    f3.metric("Forecast Bias", "Pending", help="Bias percentage")
    f4.metric("Model Baseline Target", "0.618 WAPE", help="Seasonal-Naive baseline target to beat")

    st.markdown("#### 📈 Forecast vs Historical Demand Chart Placeholder")
    st.info("Chart placeholder: Historical demand series, seasonal-naive baseline curve, and ML model (LightGBM/XGBoost) predictions will plot here upon connection.")

# -----------------------------------------------------------------------------
# PAGE 9: RECOMMENDATIONS (Pending Module UI)
# -----------------------------------------------------------------------------
elif selected_page == "9. Recommendations (Pending)":
    st.markdown("""
    <div class="pending-box">
        <h4>⏳ Advanced Recommendations Module Pending</h4>
        <p>Future recommendations will incorporate demand forecasts, lost revenue estimates, and excess stock values. Current actions below reflect <strong>CURRENT INVENTORY RULE-BASED STATUS ONLY</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💡 Current Rule-Based Reorder & Risk Action Fallback")
    
    if not df_inv.empty and not df_sku.empty:
        df_merged = pd.merge(df_inv, df_sku, on="sku_id", how="inner")
        df_merged["inventory_status"] = df_merged.apply(
            lambda r: classify_inventory_status(r["stock_on_hand"], r["reorder_point"], r["safety_stock"]), axis=1
        )
        
        # Current rule-based fallback recommendation mapping
        def get_fallback_action(status):
            if status == "Critical":
                return "REORDER NOW"
            elif status == "Reorder":
                return "SUPPLIER REVIEW"
            else:
                return "HEALTHY / MAINTAIN"

        df_merged["recommended_action"] = df_merged["inventory_status"].apply(get_fallback_action)
        
        act_dist = df_merged["recommended_action"].value_counts().reset_index()
        act_dist.columns = ["Recommended Action", "SKU Count"]
        
        st.plotly_chart(create_bar_chart(act_dist, x="Recommended Action", y="SKU Count", title="Rule-Based Action Distribution"), use_container_width=True)

        st.markdown("#### 📋 Action Recommendation Master Table (Ready for `recommendations.csv`)")
        st.dataframe(
            df_merged[["store_id", "sku_id", "sku_name", "category", "stock_on_hand", "reorder_point", "safety_stock", "inventory_status", "recommended_action"]].head(50),
            use_container_width=True
        )

# -----------------------------------------------------------------------------
# PAGE 10: METHODOLOGY
# -----------------------------------------------------------------------------
elif selected_page == "10. Methodology":
    st.markdown("### 📑 Project Foresight Methodology & Roadmap")
    
    st.markdown("""
    PROJECT FORESIGHT is an end-to-end demand & inventory intelligence architecture built across 10 structured project stages.
    
    #### 🚦 Stage Execution Status Matrix
    """)

    stages = [
        ("1. Data Collection", "Completed", "Gathered 4-year point-of-sale history, store master, SKU catalog, promotions & customer files."),
        ("2. Data Cleaning", "Completed", "Pre-cleaned missing values, date formats, standardized SKU IDs, and verified column schemas."),
        ("3. Exploratory Data Analysis (EDA)", "In Progress", "Analyzing demand skewness (log-normal, SKU04321 outlier), monthly seasonality (Nov/Dec peak, Feb trough)."),
        ("4. Feature Engineering", "Pending", "Building lag features (lag_7, lag_14, lag_365) and trailing rolling statistics (roll7_mean, roll28_std)."),
        ("5. Demand Forecasting", "Pending", "Training seasonal-naive baseline (target WAPE 0.618) and LightGBM / tree-based ML demand models."),
        ("6. Forecast Evaluation", "Pending", "Evaluating holdout performance (Q4 2025 holdout) across volume tiers and product categories."),
        ("7. Inventory Risk Scoring", "Pending", "Combining days-of-cover and demand percentiles for dead stock & stockout risk scoring."),
        ("8. Business Impact", "Pending", "Estimating potential lost revenue from stockouts and dead capital locked in excess inventory."),
        ("9. Action Recommendations", "Pending", "Generating automated business actions (REORDER NOW, SUPPLIER REVIEW, MARKDOWN / CLEAR)."),
        ("10. Decision-Support Dashboard", "Completed (V1 UI)", "Interactive Streamlit dashboard architecture connecting intelligence views.")
    ]

    for stage_name, status, desc in stages:
        badge_class = "badge-completed" if status == "Completed" else ("badge-reorder" if status == "In Progress" else "badge-pending")
        st.markdown(f"""
        <div style="background:#131722; padding:14px 18px; border-radius:8px; border:1px solid #2a3447; margin-bottom:10px;">
            <span class="badge {badge_class}">{status}</span> &nbsp; <strong>{stage_name}</strong>
            <p style="color:#94a3b8; margin-top:6px; margin-bottom:0; font-size:0.9rem;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)
