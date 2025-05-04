import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Streamlit config
st.set_page_config(page_title="UK Credit & Financial Inclusion", layout="wide")
st.title("🇬🇧 Credit Access and Financial Inclusion in the UK")

# Country code
country = "GB"

# World Bank Indicators and Labels
indicators = {
    "FS.AST.PRVT.GD.ZS": "Credit to Private Sector (% of GDP)",
    "FX.OWN.TOTL.ZS": "Account Ownership (% of Adults)",
    "FX.OWN.TOTL.FE.ZS": "Account Ownership (% of Women)",
    "g20.made.t.d": "Mobile Account Usage (% of Firms)",
    "FR.INR.LNDP": "Interest Rate Spread"
}

@st.cache_data(ttl=86400)
def fetch_wb_data(indicator):
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&per_page=100"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        if len(json_data) < 2:
            return pd.DataFrame()
        records = json_data[1]
        df = pd.DataFrame([
            {
                "Year": int(row["date"]),
                "Value": row["value"]
            } for row in records if row["value"] is not None
        ])
        return df.sort_values("Year")
    else:
        return pd.DataFrame()

# Create visualizations
def plot_indicator(indicator_code, label):
    df = fetch_wb_data(indicator_code)
    if df.empty:
        st.warning(f"No data available for {label}.")
    else:
        fig = px.line(df, x="Year", y="Value", markers=True,
                      labels={"Year": "Year", "Value": label},
                      title=label)
        st.plotly_chart(fig, use_container_width=True)

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Overview",
    "Credit to GDP",
    "Account Ownership",
    "Gender Inclusion",
    "Mobile Finance",
    "Interest Rate Spread",
    "Recommendations"
])

with tab1:
    st.header("📌 Overview")
    st.markdown("""
    This dashboard provides a real-time view of credit accessibility and financial inclusion in the **United Kingdom**, powered by the World Bank Indicators API.
    Key metrics tracked:
    - Domestic credit to private sector
    - Financial account ownership
    - Mobile finance uptake
    - Interest Rate Spread
    """)

with tab2:
    st.header("Credit to Private Sector")
    plot_indicator("FS.AST.PRVT.GD.ZS", indicators["FS.AST.PRVT.GD.ZS"])

with tab3:
    st.header("Account Ownership")
    plot_indicator("FX.OWN.TOTL.ZS", indicators["FX.OWN.TOTL.ZS"])

with tab4:
    st.header("Gender Inclusion in Financial Access")
    df_male = fetch_wb_data("FX.OWN.TOTL.MA.ZS")
    df_female = fetch_wb_data("FX.OWN.TOTL.FE.ZS")
    if not df_male.empty and not df_female.empty:
        merged = pd.merge(df_male, df_female, on="Year", suffixes=("_Male", "_Female"))
        merged["Gender Gap (%)"] = merged["Value_Male"] - merged["Value_Female"]
        fig = px.line(merged, x="Year", y=["Value_Male", "Value_Female"],
                      labels={"value": "Account Ownership (%)", "variable": "Group"},
                      title="Account Ownership: Male vs Women")
        st.plotly_chart(fig, use_container_width=True)

        gap_fig = px.area(merged, x="Year", y="Gender Gap (%)",
                          title="Gender Gap in Account Ownership")
        st.plotly_chart(gap_fig, use_container_width=True)
    else:
        st.warning("Insufficient gender data available.")

with tab5:
    st.header("Mobile Financial Usage")
    plot_indicator("g20.made.t.d", indicators["g20.made.t.d"])

with tab6:
    st.header("Interest Rate Spread")
    plot_indicator("FR.INR.LNDP", indicators["FR.INR.LNDP"])

with tab7:
    st.header("Recommendations")
    st.markdown("""
    ### Insights
    - UK credit to GDP is stable but slowly declining.
    - Mobile and digital finance usage is gradually rising.
    - Gender gaps in financial inclusion are small but exist.
    - Physical bank infrastructure is declining - digital-first approaches are crucial.

    ### Strategic Recommendations
    1. **Expand Mobile-First Financial Products** for sustainance and the underserved urban/rural segments.
    2. **Close the Gender Gap** through personalized campaigns and services for women.
    3. **Incentivize Fintech-Led Credit Solutions** using Open Banking and real-time data.

    > Data current as of: **April 2025** via the World Bank Indicators API.
    """)
    st.success("Built for decision-makers in policy and financial innovation.")
