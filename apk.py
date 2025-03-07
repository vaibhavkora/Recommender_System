import pickle
import streamlit as st
import requests
import time
import pandas as pd
import os

# Function to download similarity.pkl if it doesn't exist
def download_similarity():
    if not os.path.exists("similarity.pkl"):
        url = "https://github.com/vaibhavkora/Recommender_System/releases/download/v1.0.0/similarity.pkl"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            with open("similarity.pkl", "wb") as f:
                f.write(response.content)
            st.success("✅ similarity.pkl downloaded successfully!")
        except Exception as e:
            st.error(f"❌ Failed to download similarity.pkl: {e}")
            st.stop()

# Download similarity.pkl
download_similarity()

# Function to fetch movie poster using TMDb API
def fetch_poster(movie_id):
    API_KEY = "3022cc4905f479c6cbce198be9728ffc"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"

    for _ in range(3):  # Retry up to 3 times
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()

            if "poster_path" in data and data["poster_path"]:
                return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
            return "https://via.placeholder.com/500x750?text=No+Image"
        except requests.exceptions.RequestException as e:
            print(f"Retrying... Error fetching poster: {e}")
            time.sleep(3)
    return "https://via.placeholder.com/500x750?text=Error"

# Function to recommend movies
def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("❌ Movie not found in database. Please try another.")
        return [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:10]:  # Get top 9 recommendations
        movie_id = movies.at[i[0], 'movie_id']
        movie_name = movies.at[i[0], 'title']

        if pd.isna(movie_id) or pd.isna(movie_name):
            continue

        poster_url = fetch_poster(movie_id)
        recommended_movie_posters.append(poster_url)
        recommended_movie_names.append(movie_name)

    return recommended_movie_names, recommended_movie_posters

# Streamlit UI Configuration
st.set_page_config(page_title="Movie Recommender", layout="wide")

# Custom CSS Styling
st.markdown("""
    <style>
    .big-font {
        font-size: 32px !important;
        font-weight: bold !important;
        color: #FF4B4B !important;
        text-align: center;
        margin-bottom: 30px;
    }
    .movie-card {
        padding: 15px;
        border-radius: 10px;
        background: #0E1117;
        transition: transform 0.3s;
        margin: 10px;
    }
    .movie-card:hover {
        transform: scale(1.05);
        background: #1A1D24;
    }
    .movie-title {
        font-size: 18px !important;
        font-weight: bold !important;
        color: white !important;
        text-align: center;
        margin-top: 10px;
    }
    .stSelectbox > div > div {
        background-color: #0E1117;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Main App
st.markdown('<p class="big-font">🎬 Movie Recommendation Engine</p>', unsafe_allow_html=True)

# Load data
try:
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("❌ Data files missing! Ensure 'movie_list.pkl' and 'similarity.pkl' exist.")
    st.stop()

# Movie selection
selected_movie = st.selectbox(
    "🔍 Search your favorite movie:",
    movies['title'].dropna().unique(),
    index=0,
    help="Start typing to search movies"
)

if st.button("🚀 Get Recommendations", use_container_width=True):
    names, posters = recommend(selected_movie)
    
    if names:
        # Create responsive columns
        cols = st.columns(len(names))
        
        for col, name, poster in zip(cols, names, posters):
            with col:
                st.markdown(f'<div class="movie-card">', unsafe_allow_html=True)
                st.image(
                    poster,
                    use_container_width=True,  # Corrected parameter
                    caption="",
                    width=300
                )
                st.markdown(f'<div class="movie-title">{name}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("No recommendations found for this movie.")

# Footer
st.markdown("---")
st.markdown("""
    <style>
    .footer {
        text-align: center;
        padding: 10px;
        color: #666;
    }
    </style>
    <div class="footer">
        Movie data powered by TMDb API | Built with Streamlit
    </div>
    """, unsafe_allow_html=True)
