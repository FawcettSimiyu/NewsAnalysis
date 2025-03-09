import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import json

# Load API key from a separate file
def load_api_key():
    with open("api_key.json", "r") as file:
        data = json.load(file)
    return data["NYT_API_KEY"]

API_KEY = load_api_key()
BASE_URL = "https://api.nytimes.com/svc/topstories/v2/{}.json"

# Function to fetch articles
def fetch_articles(section):
    url = BASE_URL.format(section)
    params = {"api-key": API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        st.error("Failed to fetch articles. Check your API key and internet connection.")
        return []

# Extract relevant article data
def extract_data(articles):
    data = []
    for article in articles:
        keywords = [kw["value"] for kw in article.get("des_facet", [])]
        data.append({
            "title": article["title"],
            "published_date": article["published_date"].split("T")[0],
            "keywords": ", ".join(keywords)
        })
    return pd.DataFrame(data)

# Keyword frequency analysis
def analyze_keywords(df):
    all_keywords = ", ".join(df["keywords"].dropna()).split(", ")
    keyword_counts = pd.Series(all_keywords).value_counts().head(10)
    return keyword_counts

# Visualization functions
def plot_keyword_frequency(keyword_counts):
    plt.figure(figsize=(10, 5))
    sns.barplot(x=keyword_counts.values, y=keyword_counts.index, palette="Blues")
    plt.xlabel("Frequency")
    plt.ylabel("Keywords")
    plt.title("Top Keywords in Selected Section")
    st.pyplot(plt)

def plot_articles_over_time(df):
    df["published_date"] = pd.to_datetime(df["published_date"])
    df_grouped = df.groupby(df["published_date"].dt.date).count()
    plt.figure(figsize=(10, 5))
    plt.plot(df_grouped.index, df_grouped["title"], marker="o", linestyle="-", color="blue")
    plt.xlabel("Date")
    plt.ylabel("Number of Articles")
    plt.title("Articles Published Over Time")
    plt.xticks(rotation=45)
    st.pyplot(plt)

# Streamlit UI
st.title("New York Times News Analysis")

# User inputs
section = st.selectbox("Select News Section:", ["technology", "politics", "business", "health", "science", "sports"])
if st.button("Fetch & Analyze News"):
    articles = fetch_articles(section)
    if articles:
        df = extract_data(articles)
        st.write(df)
        
        keyword_counts = analyze_keywords(df)
        st.subheader("Keyword Frequency Analysis")
        plot_keyword_frequency(keyword_counts)
        
        st.subheader("Articles Published Over Time")
        plot_articles_over_time(df)

