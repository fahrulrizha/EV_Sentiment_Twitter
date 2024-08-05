from st_pages import hide_pages
import streamlit as st
import mysql.connector
import pandas as pd
import pymysql
import matplotlib.pyplot as plt
from datetime import datetime

# Hide specific pages
hide_pages(["Dashboard", "Import", "Preprocessing", "Labelling", "Classify", "option"])

# Connect to MySQL database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',  
    database='dbl',
)
cursor = conn.cursor()

def display_sentiment_count(df):
    """
    Function to display sentiment counts.
    """
    sentiment_counts = df['prediction'].value_counts()
    st.write("Sentiment Counts:")
    st.write(sentiment_counts)


def search_data(conn, search_term):
    """
    Function to search data based on the given search term.
    """
    try:
        with conn.cursor() as cursor:
            search_query = "SELECT c.stemming_data AS text, c.actual, c.prediction, t.created_at FROM class c JOIN tweets t ON c.tweet_id = t.tweet_id WHERE c.stemming_data LIKE %s;"
            cursor.execute(search_query, ('%' + search_term + '%',))
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['text', 'actual', 'prediction', 'created_at'])

            if not df.empty:
                st.write(f"Search Results for '{search_term}':")
                sentiment_counts = df['prediction'].value_counts()
                st.write("Sentiment Counts:")
                st.write(sentiment_counts)
                st.dataframe(df)

                # Visualize sentiment predictions with a pie chart
                st.write("Sentiment Distribution:")
                fig, ax = plt.subplots()
                ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=140)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                st.pyplot(fig)
            else:
                st.warning(f"No results found for '{search_term}'.")

            return df

    except pymysql.Error as e:
        st.error(f"Error fetching data: {e}")

def show_data(conn):
    try:
        with conn.cursor() as cursor:
            select_query = "SELECT c.stemming_data AS text, c.actual, c.prediction, t.created_at FROM class c JOIN tweets t ON c.tweet_id = t.tweet_id;"
            cursor.execute(select_query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['text', 'actual', 'prediction', 'created_at'])

            if not df.empty:
                st.write("All Data:")
                st.dataframe(df)

                # Filter by month
                #filter_by_month(df)

                # Display sentiment counts and pie chart
                display_sentiment_count(df)
                st.write("Sentiment Distribution:")
                fig, ax = plt.subplots()
                ax.pie(df['prediction'].value_counts(), labels=df['prediction'].value_counts().index, autopct='%1.1f%%', startangle=140)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                st.pyplot(fig)
            else:
                st.warning("No data available to show.")
    except pymysql.Error as e:
        st.error(f"Error fetching data: {e}")

def filter_by_month(df):
    """
    Function to filter data by selected month and year.
    """
    st.header("Filter Data by Month and Year")

    # Extract unique months and years from the 'created_at' column
    df['created_at'] = pd.to_datetime(df['created_at'])  # Ensure 'created_at' is in datetime format
    df['year_month'] = df['created_at'].dt.to_period('M')  # Create a new column with year and month
    
    year_months = df['year_month'].sort_values().unique()
    selected_year_month = st.selectbox("Select a month and year", year_months)

    # Extract selected month and year from the selection
    selected_month = selected_year_month.month
    selected_year = selected_year_month.year

    # Filter the dataframe based on selected month and year
    filtered_df = df[(df['created_at'].dt.month == selected_month) & (df['created_at'].dt.year == selected_year)]
    st.dataframe(filtered_df)


# Add image background
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("https://images.unsplash.com/photo-1528235815879-8492a727d628?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1500&q=80");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit interface
st.markdown("<h1 style='text-align: center;'>EV Sentiment Analysis</h1>", unsafe_allow_html=True)

# Search Data
st.header('Search Data')
search_term = st.text_input('Enter search term')
if search_term:
    df = search_data(conn, search_term)
    if not df.empty:
        filter_by_month(df)

# Button to show all data
if st.button('Show All Data'):
    show_data(conn)
