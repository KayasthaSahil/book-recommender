from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import os
from pathlib import Path
from dotenv import load_dotenv
from controllers.recommendation_controller import get_best_recommendations

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv(override=False)

# Configure paths
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / 'models'
DATA_DIR = BASE_DIR / 'data'

# Load the pre-trained models and data
try:
    popular_df = pickle.load(open(MODELS_DIR / 'popular.pkl', 'rb'))
    pt = pickle.load(open(MODELS_DIR / 'pt.pkl', 'rb'))
    books = pickle.load(open(MODELS_DIR / 'books.pkl', 'rb'))
    similarity_scores = pickle.load(open(MODELS_DIR / 'similarity_scores.pkl', 'rb'))
except FileNotFoundError as e:
    print(f"Error loading model files: {e}")
    print("Please ensure all .pkl files are present in the models directory")
    raise

@app.route('/')
def index():
    return render_template('index.html',
                         popular_books=list(zip(
                             popular_df['Book-Title'].values,
                             popular_df['Book-Author'].values,
                             popular_df['Image-URL-M'].values,
                             popular_df['num_ratings'].values,
                             popular_df['avg_rating'].values
                         )))

@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify([])
    
    try:
        # Search in book titles
        matching_books = books[books['Book-Title'].str.lower().str.contains(query, na=False)]
        results = []
        for _, book in matching_books.head(5).iterrows():
            results.append({
                'title': book['Book-Title'],
                'author': book['Book-Author']
            })
        return jsonify(results)
    except Exception as e:
        print(f"Error in search: {e}")
        return jsonify([])

@app.route('/recommend')
def recommend_form():
    return render_template('recommend.html')

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    book_name = request.form.get('book_name')
    if not book_name:
        return render_template('error.html', message="Please enter a book title")

    try:
        result = get_best_recommendations(book_name, pt=pt, books=books, similarity_scores=similarity_scores)
        source = result.get('source', 'none')
        items = result.get('items', [])

        if not items:
            return render_template('error.html', message="No recommendations available right now. Please try another book or try again later.")

        return render_template(
            'recommendations.html',
            recommendations=items,
            selected_book=book_name,
            source=source
        )
    except Exception as e:
        print(f"Error in recommendations: {e}")
        return render_template('error.html', message="An error occurred while getting recommendations. Please try again.")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', 
                         message="The page you're looking for doesn't exist."), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', 
                         message="An internal server error occurred. Please try again later."), 500

if __name__ == '__main__':
    app.run(debug=True) 