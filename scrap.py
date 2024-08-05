import streamlit as st
import pandas as pd
import mysql.connector
from tweet_harvest import TweetHarvest

# Function to connect to MySQL
def connect_to_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="scrap"
    )

# Main function to fetch and store data
def main():
    st.title('Twitter Data Scraping and Storage')

    # Twitter Auth Token
    twitter_auth_token = st.text_input("Twitter Auth Token")

    # Search keyword
    search_keyword = st.text_input("Search Keyword", value=" lang:id")

    # Limit
    limit = st.number_input("Limit", value=30)

    # Button to start scraping
    if st.button("Start Scraping"):
        st.info("Scraping tweets...")

        # Initialize TweetHarvest
        th = TweetHarvest(auth_token=twitter_auth_token)

        # Fetch tweets
        tweets = th.search_tweets(q=search_keyword, limit=limit)

        # Connect to MySQL
        conn = connect_to_mysql()
        cursor = conn.cursor()

        # Create table
        cursor.execute("""CREATE TABLE IF NOT EXISTS tweets (
                            tweet_id BIGINT PRIMARY KEY,
                            tweet_text TEXT,
                            user_id BIGINT,
                            user_name VARCHAR(255),
                            created_at DATETIME
                         )""")

        # Insert data into MySQL
        for tweet in tweets:
            cursor.execute("""INSERT INTO tweets (tweet_id, tweet_text, user_id, user_name, created_at) 
                              VALUES (%s, %s, %s, %s, %s)""", 
                           (tweet.id, tweet.text, tweet.user.id, tweet.user.name, tweet.created_at))
        conn.commit()

        st.success("Data successfully stored in MySQL.")

        # Convert tweets to DataFrame for display
        df = pd.DataFrame([{'tweet_id': tweet.id, 'tweet_text': tweet.text, 'user_id': tweet.user.id,
                            'user_name': tweet.user.name, 'created_at': tweet.created_at} for tweet in tweets])

        # Display DataFrame
        st.write(df)

if __name__ == "__main__":
    main()