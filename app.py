import os
import requests
import streamlit as st
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import gtts
from deep_translator import GoogleTranslator

# Download necessary NLTK data
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()
translator = GoogleTranslator(source='auto', target='hi')

def get_news(company):
    """Fetch at least 10 news articles using NewsAPI"""
    api_key = "6672940d97c248eeaa6f503e792362c2"  # Your API Key
    url = f"https://newsapi.org/v2/everything?q={company}&language=en&apiKey={api_key}"
    
    response = requests.get(url)
    data = response.json()

    articles = []
    if "articles" in data:
        for item in data["articles"][:10]:  # Get the top 10 news articles
            title = item["title"]
            description = item["description"] if item["description"] else "No description available."
            articles.append({"title": title, "description": description})

    return articles

def analyze_sentiment(text):
    """Perform sentiment analysis on text"""
    sentiment_score = sia.polarity_scores(text)
    if sentiment_score['compound'] >= 0.05:
        return "Positive"
    elif sentiment_score['compound'] <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def generate_tts(text, filename="output.mp3"):
    """Convert text summary to Hindi speech"""
    translated_text = translator.translate(text)
    tts = gtts.gTTS(translated_text, lang="hi")
    tts.save(filename)
    return filename

# Streamlit UI
st.title("📢 News Summarization and Hindi Speech Generator")
company = st.text_input("Enter Company Name")

if st.button("🔍 Get News"):
    news_articles = get_news(company)
    
    if news_articles:
        st.subheader(f"📄 News Articles for {company}")
        structured_data = {"Company": company, "Articles": [], "Sentiment Summary": {}}
        positive, negative, neutral = 0, 0, 0
        news_summary = ""

        for article in news_articles:
            sentiment = analyze_sentiment(article['title'])
            structured_data["Articles"].append({
                "Title": article["title"],
                "Description": article["description"],
                "Sentiment": sentiment
            })
            
            news_summary += f"• {article['title']} ({sentiment})\n"

            if sentiment == "Positive":
                positive += 1
            elif sentiment == "Negative":
                negative += 1
            else:
                neutral += 1
        
        structured_data["Sentiment Summary"] = {
            "Positive": positive,
            "Negative": negative,
            "Neutral": neutral
        }

        # Display results as bullet points
        for article in structured_data["Articles"]:
            st.write(f"• **{article['Title']}** ({article['Sentiment']})")
            st.write(f"📝 {article['Description']}")
            st.write("---")  # Separator for better readability
        
        # Display Sentiment Summary
        st.subheader("📊 Overall Sentiment Summary")
        st.write(f"✅ **Positive:** {positive}  ❌ **Negative:** {negative}  ⚖️ **Neutral:** {neutral}")

        # Generate Hindi TTS Summary
        summary_text = f"According to the news analysis for {company}, the number of positive news articles is {positive}, negative {negative}, and neutral {neutral}. The news points are as follows: {news_summary}"
        tts_file = generate_tts(summary_text)
        
        # Play Hindi Speech
        st.subheader("🔊 Hindi Audio Summary")
        st.audio(tts_file)
    else:
        st.error("❌ No news articles found.")
