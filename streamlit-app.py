import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Set page config
st.set_page_config(page_title="Credit Access in India", layout="wide")

st.title("🇮🇳 Credit Access and Financial Inclusion in India (Dynamic Dashboard)")

# Helper function to fetch World Bank data
@st.cache_data(ttl=86400)
def fetch_worldbank_data(indicator):
    url = f"http://api.worldbank.org/v2/country/IN/indicator/{indicator}?format=json&per_page=100"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data and len(data) > 1:
            df = pd.json_normalize(data[1])
            df = df[['date', 'value']]
            df.columns = ['Year', indicator]
            df.dropna(inplace=True)
            df['Year'] = df['Year'].astype(int)
            return df.sort_values('Year')
    return pd.DataFrame()

# Load dynamic data
credit_gdp_df = fetch_worldbank_data("FS.AST.PRVT.GD.ZS")  # Domestic credit to private sector
account_access_df = fetch_worldbank_data("FX.OWN.TOTL.ZS")  # Account ownership
female_access_df = fetch_worldbank_data("FX.OWN.TOTL.FE.ZS")  # Female account ownership

# Layout tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview", 
    "Credit vs GDP", 
    "Account Ownership", 
    "Gender Gap", 
    "Trend Analysis", 
    "Recommendation"
])

with tab1:
    st.header("📌 Overview of Financial Inclusion Indicators")
    st.markdown("""
    This dashboard visualizes the state of **credit provision** and **financial inclusion** in India using real-time data from the World Bank. 
    We explore trends in credit-to-GDP ratio, account ownership among adults, and gender disparities in access to financial services.
    
    **Objective**: Provide data-backed, decision-oriented insights to improve financial inclusion and credit accessibility in India.
    """)

with tab2:
    st.header("💰 Domestic Credit to Private Sector (% of GDP)")
    if not credit_gdp_df.empty:
        fig = px.line(credit_gdp_df, x="Year", y="FS.AST.PRVT.GD.ZS", 
                      title="Domestic Credit to Private Sector (% of GDP)", markers=True)
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Latest Value", 
                  f"{credit_gdp_df.iloc[-1]['FS.AST.PRVT.GD.ZS']:.2f}%", 
                  delta=f"{credit_gdp_df.iloc[-1]['FS.AST.PRVT.GD.ZS'] - credit_gdp_df.iloc[-2]['FS.AST.PRVT.GD.ZS']:.2f}")
    else:
        st.warning("Data not available.")

with tab3:
    st.header("🏦 Account Ownership (% of Adults 15+)")
    if not account_access_df.empty:
        fig = px.line(account_access_df, x="Year", y="FX.OWN.TOTL.ZS", 
                      title="Account Ownership - Total Adult Population", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Data not available.")

with tab4:
    st.header("👩‍🦰 Gender Gap in Account Ownership")
    if not account_access_df.empty and not female_access_df.empty:
        merged_df = pd.merge(account_access_df, female_access_df, on="Year", how="inner")
        merged_df["Gender Gap"] = merged_df["FX.OWN.TOTL.ZS"] - merged_df["FX.OWN.TOTL.FE.ZS"]
        fig = px.line(merged_df, x="Year", y=["FX.OWN.TOTL.ZS", "FX.OWN.TOTL.FE.ZS"], 
                      labels={"value": "Account Ownership (%)", "variable": "Group"},
                      title="Male vs Female Account Ownership", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        fig_gap = px.area(merged_df, x="Year", y="Gender Gap", title="Gender Gap Over Time")
        st.plotly_chart(fig_gap, use_container_width=True)
    else:
        st.warning("Gender data not available.")

with tab5:
    st.header("📈 Credit vs Financial Inclusion Correlation")
    if not credit_gdp_df.empty and not account_access_df.empty:
        merged_corr = pd.merge(credit_gdp_df, account_access_df, on="Year", how="inner")
        fig_corr = px.scatter(merged_corr, 
                              x="FX.OWN.TOTL.ZS", 
                              y="FS.AST.PRVT.GD.ZS",
                              trendline="ols",
                              labels={
                                  "FX.OWN.TOTL.ZS": "Account Ownership (%)", 
                                  "FS.AST.PRVT.GD.ZS": "Credit to Private Sector (% of GDP)"
                              },
                              title="Relationship Between Account Access and Credit Provision")
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning("Insufficient data to show correlation.")

with tab6:
    st.header("✅ Actionable Recommendation")
    st.markdown("""
    ### 🔍 Insight
    While account ownership in India has improved markedly, **credit access remains comparatively constrained**. 
    There's also a notable **gender gap** in financial services participation.

    ### 📌 Strategic Recommendations:
    **1. Expand Inclusive Credit Infrastructure**
    - Boost rural and small-town credit availability via digital KYC, microloans, and fintech partnerships.
    - Incentivize banks and NBFCs to reach underbanked groups through targeted SLAs.

    **2. Gender-Targeted Interventions**
    - Deploy subsidized loan products tailored to **women-led MSMEs**.
    - Fund community-based financial education programs focused on women.

    **3. Build on Digital Rails**
    - Use UPI and Aadhaar to simplify and fast-track loan disbursements.
    - Enable alternative credit scoring (via bill payments, mobile top-ups) to reduce bias in loan decisions.

    ### 🎯 Outcome
    These measures can:
    - Strengthen GDP-credit ratios,
    - Improve equity in financial access,
    - Support ESG-aligned sustainable development.
    """)
    st.success("Insights based on World Bank data up to April 2025.")
