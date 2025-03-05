import pickle
import streamlit as st
import requests
import time
import pandas as pd


# Function to fetch movie poster using TMDb API
def fetch_poster(movie_id):
    API_KEY = "3022cc4905f479c6cbce198be9728ffc"  # Replace with your TMDb API Key
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"

    for _ in range(3):  # Retry up to 3 times
        try:
            response = requests.get(url, timeout=20)  # Set timeout
            response.raise_for_status()  # Raise error if request fails
            data = response.json()

            if "poster_path" in data and data["poster_path"]:
                return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
            else:
                return "https://via.placeholder.com/500x750?text=No+Image"  # Placeholder image

        except requests.exceptions.RequestException as e:
            print(f"Retrying... Error fetching poster: {e}")
            time.sleep(3)  # Wait before retrying

    return "https://via.placeholder.com/500x750?text=Error"  # Return error image after retries fail


# Function to recommend movies based on similarity
def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("❌ Movie not found in database. Please try another.")
        return [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:  # Get top 5 recommended movies
        movie_id = movies.at[i[0], 'movie_id']  # Use .at instead of .iloc for safety
        movie_name = movies.at[i[0], 'title']

        if pd.isna(movie_id) or pd.isna(movie_name):  # Skip missing data
            continue

        poster_url = fetch_poster(movie_id)
        recommended_movie_posters.append(poster_url)
        recommended_movie_names.append(movie_name)

    return recommended_movie_names, recommended_movie_posters


# Streamlit UI
st.header("🎬 Movie Recommender System")

# Load movie data
try:
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("❌ Movie data files not found! Make sure 'movie_list.pkl' and 'similarity.pkl' exist.")
    st.stop()  # Stop execution if files are missing

# Ensure movies data is a DataFrame
if not isinstance(movies, pd.DataFrame):
    st.error("❌ Invalid movie data format! Ensure 'movie_list.pkl' contains a DataFrame.")
    st.stop()

movie_list = movies['title'].dropna().unique()  # Remove NaN values & duplicates
selected_movie = st.selectbox("🔎 Select a movie", movie_list)

if st.button("Show Recommendations"):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    if recommended_movie_names:
        cols = st.columns(len(recommended_movie_names))  # Dynamically adjust columns
        for col, name, poster in zip(cols, recommended_movie_names, recommended_movie_posters):
            with col:
                st.text(name)
                st.image(poster)