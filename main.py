import pandas as pd
import matplotlib.pyplot as plt
import panel as pn

pn.extension()

# --- 1. Load and clean data ---
df = pd.read_csv("data.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df["date_created"] = pd.to_datetime(df["date_created"])
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

# --- 2. Plot 1: Success / Fail % by Region (all regions) ---
counts_region = df.groupby(['id_region', 'status'])['id_user'].count().unstack(fill_value=0)
percent_region = counts_region.div(counts_region.sum(axis=1), axis=0) * 100

fig1, ax1 = plt.subplots(figsize=(8, 4))
percent_region.plot(kind='bar', stacked=True, ax=ax1)
ax1.set_ylabel("Percentage (%)")
ax1.set_title("Success / Fail % by Region")

for container in ax1.containers:
    labels = [f'{v:.1f}%' for v in container.datavalues]
    ax1.bar_label(container, labels=labels, label_type='center')


# --- 3. Plot 2: Time-series of Fail Rates by Date ---
daily = df.groupby(df["date_created"].dt.date).agg(
    total_orders=('id_order', 'count'),
    total_fails=('status', lambda s: (s == 'fail').sum())
).reset_index()
daily["pct_fails_of_fails"] = 100 * daily["total_fails"] / daily["total_fails"].sum()
daily["pct_fails_of_orders"] = 100 * daily["total_fails"] / daily["total_orders"]

fig2, ax2 = plt.subplots(figsize=(8, 4))
ax2.plot(daily["date_created"], daily["pct_fails_of_fails"], label="% fails of all fails")
ax2.plot(daily["date_created"], daily["pct_fails_of_orders"], label="% fails of all orders")
ax2.set_xlabel("Date")
ax2.set_ylabel("Percentage (%)")
ax2.set_title("Daily Fail Rate (relative to fails and orders)")
ax2.legend()

# --- 4. Plot 3: Daily Fail % by Region over Time ---
region_daily = df.groupby([df["date_created"].dt.date, "id_region"]).agg(
    fails=('status', lambda s: (s == 'fail').sum()),
    orders=('id_order', 'count')
).reset_index()
region_daily["pct_fail_region"] = 100 * region_daily["fails"] / region_daily["orders"]

fig3, ax3 = plt.subplots(figsize=(8, 4))
for region in sorted(region_daily["id_region"].unique()):
    subset = region_daily[region_daily["id_region"] == region]
    ax3.plot(subset["date_created"], subset["pct_fail_region"], label=f"Region {region}")
ax3.set_xlabel("Date")
ax3.set_ylabel("Fail %")
ax3.set_title("Daily Fail % by Region (All Regions)")
ax3.legend()

# --- 5. Create Panel layout with all plots ---
dashboard = pn.Column(
    pn.pane.Matplotlib(fig1, tight=True),
    pn.pane.Matplotlib(fig2, tight=True),
    pn.pane.Matplotlib(fig3, tight=True)
)

# --- 6. Save as static HTML with embedded state ---
dashboard.save('dashboard_all.html', embed=True)
