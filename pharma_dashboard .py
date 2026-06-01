
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# DATA LOAD
df = pd.read_csv("sales_data.csv", encoding="latin1")

# DATA CLEANING
df.columns = df.columns.str.strip()
df["Calendar Day"] = pd.to_datetime(df["Calendar Day"], errors="coerce")
df["Month"] = df["Calendar Day"].dt.month
df["Year"] = df["Calendar Day"].dt.year
df["Week"] = df["Calendar Day"].dt.isocalendar().week.astype(int)

df["SalesValue"] = (
    df["SalesValue"].astype(str)
    .str.replace(r"[^\d.]", "", regex=True)
    .pipe(pd.to_numeric, errors="coerce")
)
df["SalesQty"] = (
    df["SalesQty"].astype(str)
    .str.replace(r"[^\d.]", "", regex=True)
    .pipe(pd.to_numeric, errors="coerce")
)
df.dropna(subset=["SalesValue"], inplace=True)

# ANALYSIS
week_labels = df.groupby("Week")["Calendar Day"].min().reset_index()
week_labels["Label"] = ["Week " + str(i+1) + " (" + d.strftime("%d %b") + ")"
                         for i, d in enumerate(week_labels["Calendar Day"])]
weekly_sales = df.groupby("Week")["SalesValue"].sum().reset_index()
weekly_sales = weekly_sales.merge(week_labels[["Week","Label"]], on="Week")

brand_sales = df.groupby("Brand")["SalesValue"].sum().reset_index().sort_values("SalesValue", ascending=False).head(10)
brand_sales["Brand_short"] = brand_sales["Brand"].str.split().str[0]

district_sales = df.groupby("Sales District")["SalesValue"].sum().reset_index().sort_values("SalesValue", ascending=False)
customer_sales = df.groupby("Customer group 1")["SalesValue"].sum().reset_index().sort_values("SalesValue", ascending=False).head(8)

brand_pie = df.groupby("Brand")["SalesValue"].sum().reset_index()
brand_pie["Brand_short"] = brand_pie["Brand"].str.split().str[0]
brand_pie = brand_pie.sort_values("SalesValue", ascending=False)
top8 = brand_pie.head(8)
others_val = brand_pie.iloc[8:]["SalesValue"].sum()
others_row = pd.DataFrame([{"Brand": "Others", "SalesValue": others_val, "Brand_short": "Others"}])
brand_pie_final = pd.concat([top8, others_row], ignore_index=True)

qty_by_brand = df.groupby("Brand")["SalesQty"].sum().reset_index().sort_values("SalesQty", ascending=False).head(10)
qty_by_brand["Brand_short"] = qty_by_brand["Brand"].str.split().str[0]

# DASHBOARD
COLORS = ["#4e8df5","#50e3c2","#f5a623","#e74c3c","#9b59b6",
          "#1abc9c","#e67e22","#3498db","#e91e63","#00bcd4"]

fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        "Weekly Sales Trend", "Sales by Brand (Top 10)",
        "Sales by District", "Sales by Customer Group",
        "Sales Share by Brand", "Quantity Sold by Brand (Top 10)"
    ),
    specs=[
        [{"type": "scatter"}, {"type": "bar"}],
        [{"type": "bar"},     {"type": "bar"}],
        [{"type": "pie"},     {"type": "bar"}],
    ],
    vertical_spacing=0.12,
    horizontal_spacing=0.08
)

fig.add_trace(go.Scatter(
    x=weekly_sales["Label"], y=weekly_sales["SalesValue"],
    mode="lines+markers+text", name="Weekly Sales",
    line=dict(color="#4e8df5", width=2.5), marker=dict(size=9),
    text=weekly_sales["SalesValue"].apply(lambda x: f"{x/1e6:.1f}M"),
    textposition="top center", textfont=dict(color="white", size=10),
    fill="tozeroy", fillcolor="rgba(78,141,245,0.15)"
), row=1, col=1)

fig.add_trace(go.Bar(
    x=brand_sales["Brand_short"], y=brand_sales["SalesValue"],
    marker_color=COLORS[:len(brand_sales)]
), row=1, col=2)

fig.add_trace(go.Bar(
    x=district_sales["SalesValue"], y=district_sales["Sales District"],
    orientation="h", marker_color="#50e3c2"
), row=2, col=1)

fig.add_trace(go.Bar(
    x=customer_sales["Customer group 1"], y=customer_sales["SalesValue"],
    marker_color="#f5a623"
), row=2, col=2)

fig.add_trace(go.Pie(
    labels=brand_pie_final["Brand_short"], values=brand_pie_final["SalesValue"],
    hole=0.4, marker_colors=COLORS,
    textinfo="label+percent", textfont=dict(size=10)
), row=3, col=1)

fig.add_trace(go.Bar(
    x=qty_by_brand["Brand_short"], y=qty_by_brand["SalesQty"],
    marker_color="#9b59b6"
), row=3, col=2)

fig.update_layout(
    title=dict(text="<b>Pharmaceutical Sales Interactive Dashboard</b>",
               font=dict(size=20, color="white"), x=0.5),
    paper_bgcolor="#1a1a2e", plot_bgcolor="#16213e",
    font=dict(color="white", size=11),
    height=1000, showlegend=False,
    margin=dict(t=80, b=40, l=60, r=40)
)
fig.update_xaxes(gridcolor="#333366", color="white", tickfont=dict(size=9))
fig.update_yaxes(gridcolor="#333366", color="white", tickfont=dict(size=9))
for ann in fig.layout.annotations:
    ann.font.color = "white"
    ann.font.size = 13

fig.write_html("sales_dashboard.html")
fig.show()
