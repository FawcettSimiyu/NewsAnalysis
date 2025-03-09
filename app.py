import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from config import NYT_API_KEY

# Set page config
st.set_page_config(page_title="NYT News Analyzer", page_icon="📰", layout="wide")

# Custom CSS to improve UI
st.markdown(
    """
    <style>
        .main { background-color: #f8f9fa; }
        h1 { color: #2C3E50; text-align: center; }
        .css-1d391kg { padding-top: 2rem; }
        .st-bq { background-color: #e3f2fd; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True
)

# Fetch articles from NYT API
def fetch_articles(section, start_date, end_date):
    url = f"https://api.nytimes.com/svc/search/v2/articlesearch.json"
    articles = []

    for date in pd.date_range(start=start_date, end=end_date):
        params = {
            "fq": f"section_name:(\"{section}\")",
            "begin_date": date.strftime("%Y%m%d"),
            "end_date": date.strftime("%Y%m%d"),
            "api-key": NYT_API_KEY
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            docs = data["response"]["docs"]
            for doc in docs:
                articles.append({
                    "headline": doc["headline"]["main"],
                    "pub_date": doc["pub_date"][:10],
                    "keywords": [kw["value"] for kw in doc["keywords"]],
                    "summary": doc["abstract"],
                    "url": doc["web_url"]
                })

    return pd.DataFrame(articles)

# Analyze keyword frequency
def analyze_keywords(df):
    all_keywords = [kw for sublist in df["keywords"] for kw in sublist]
    keyword_counts = pd.Series(all_keywords).value_counts()
    return keyword_counts

# Title
st.title("📰 New York Times News Analyzer")

# Sidebar
st.sidebar.header("Settings")
section = st.sidebar.selectbox("Select News Section:", ["Technology", "Politics", "Science", "Health", "Business"])
start_date = st.sidebar.date_input("Start Date", datetime.today() - timedelta(days=7))
end_date = st.sidebar.date_input("End Date", datetime.today())
search_keyword = st.sidebar.text_input("🔍 Search Keyword (Optional)")

if st.sidebar.button("Fetch Articles"):
    st.sidebar.success("Fetching articles...")

    # Fetch data
    df = fetch_articles(section, start_date, end_date)

    if not df.empty:
        st.success(f"✅ Retrieved {len(df)} articles from **{section}**.")

        # Display articles in a scrollable box
        with st.expander("📝 View Articles", expanded=False):
            for _, row in df.iterrows():
                st.markdown(f"**[{row['headline']}]({row['url']})** ({row['pub_date']})")
                st.write(row["summary"])

        # Filter articles by keyword (if provided)
        if search_keyword:
            df = df[df["headline"].str.contains(search_keyword, case=False, na=False)]
            st.info(f"🔍 Found {len(df)} articles containing **'{search_keyword}'**.")

        # Keyword analysis
        keyword_counts = analyze_keywords(df)
        st.subheader("📊 Most Frequent Keywords")
        fig1 = px.bar(
            keyword_counts.head(10),
            x=keyword_counts.head(10).index,
            y=keyword_counts.head(10).values,
            labels={"x": "Keyword", "y": "Frequency"},
            title="Top 10 Most Frequent Keywords",
            color=keyword_counts.head(10).values,
            color_continuous_scale="blues"
        )
        st.plotly_chart(fig1)

        # Articles over time trend
        df["pub_date"] = pd.to_datetime(df["pub_date"])
        articles_per_day = df.groupby(df["pub_date"].dt.date).size()

        st.subheader("📈 Articles Published Over Time")
        fig2 = px.line(
            x=articles_per_day.index,
            y=articles_per_day.values,
            markers=True,
            labels={"x": "Date", "y": "Number of Articles"},
            title="Publication Trend",
            line_shape="spline"
        )
        st.plotly_chart(fig2)

    else:
        st.warning("❌ No articles found for the selected criteria.")

