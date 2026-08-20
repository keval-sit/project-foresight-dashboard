import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Consistent Dark Theme Palette
DARK_BG = "#131722"
PAPER_BG = "#0e1117"
FONT_COLOR = "#e0e6ed"
ACCENT_BLUE = "#4facfe"
ACCENT_CYAN = "#00f2fe"
COLOR_CRITICAL = "#ff5252"
COLOR_REORDER = "#ff9f43"
COLOR_HEALTHY = "#00b894"

PLOTLY_LAYOUT = dict(
    paper_bgcolor=PAPER_BG,
    plot_bgcolor=DARK_BG,
    font=dict(color=FONT_COLOR, family="Inter, sans-serif"),
    margin=dict(l=40, r=40, t=50, b=40),
    xaxis=dict(gridcolor="#2a2e3d", zerolinecolor="#2a2e3d"),
    yaxis=dict(gridcolor="#2a2e3d", zerolinecolor="#2a2e3d")
)

def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str = None, orientation: str = "v", color_map: dict = None):
    """Creates a standardized dark-themed bar chart."""
    fig = px.bar(
        df, x=x, y=y, title=title, color=color,
        orientation=orientation, color_discrete_map=color_map,
        color_discrete_sequence=[ACCENT_BLUE, ACCENT_CYAN, "#6c5ce7", "#a29bfe"]
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def create_pie_chart(df: pd.DataFrame, names: str, values: str, title: str, color_map: dict = None):
    """Creates a standardized dark-themed donut/pie chart."""
    fig = px.pie(
        df, names=names, values=values, title=title, hole=0.4,
        color=names, color_discrete_map=color_map,
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def create_stock_vs_reorder_chart(df: pd.DataFrame, title: str = "Stock on Hand vs Reorder Point"):
    """Creates a grouped bar chart comparing Stock on Hand vs Reorder Point vs Safety Stock."""
    fig = go.Figure()
    
    sample_df = df.head(15)  # Limit to top SKUs for readability
    
    fig.add_trace(go.Bar(
        x=sample_df["sku_name"], y=sample_df["stock_on_hand"],
        name="Stock on Hand", marker_color=ACCENT_CYAN
    ))
    fig.add_trace(go.Bar(
        x=sample_df["sku_name"], y=sample_df["reorder_point"],
        name="Reorder Point", marker_color=COLOR_REORDER
    ))
    fig.add_trace(go.Bar(
        x=sample_df["sku_name"], y=sample_df["safety_stock"],
        name="Safety Stock", marker_color=COLOR_CRITICAL
    ))
    
    fig.update_layout(
        bmode="group", title=title,
        xaxis_tickangle=-45,
        **PLOTLY_LAYOUT
    )
    return fig

def create_promo_timeline(df_promotions: pd.DataFrame):
    """Creates a promotion timeline Gantt chart using start_date and end_date."""
    if df_promotions.empty:
        return go.Figure()
    
    df = df_promotions.copy()
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])
    
    fig = px.timeline(
        df, x_start="start_date", x_end="end_date", y="promo_name",
        color="promo_type", title="Promotions Timeline & Campaigns",
        hover_data=["discount_pct", "target_type", "target_value"]
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig
