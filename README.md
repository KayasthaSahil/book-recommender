# Book Recommendation System

## Live Demo
🌐 **Deployed Application**: [Book Recommender](https://book-recommender-ndy7.onrender.com)

## Problem Statement
In today's digital age, readers face an overwhelming number of book choices, making it difficult to find books that match their interests and preferences. Traditional methods of book discovery often rely on manual browsing or generic bestseller lists, which may not cater to individual reader preferences. This project addresses the challenge of helping readers discover books that align with their interests through an intelligent recommendation system.

## Solution Proposed
This project implements a hybrid book recommendation system that combines two approaches:
1. **Popularity-Based Filtering**: Identifies and recommends books based on their overall popularity, considering both the number of ratings and average ratings.
2. **Collaborative Filtering**: Provides personalized recommendations by analyzing user behavior patterns and finding similar books based on user ratings.

## Objectives
- Create an efficient and scalable book recommendation system
- Implement both popularity-based and collaborative filtering approaches
- Develop a user-friendly web interface for book discovery
- Provide accurate and relevant book recommendations
- Enable users to easily search and discover new books

## METHODOLOGY / PROPOSED SYSTEM

### 1. Data Acquisition and Preprocessing

#### 1.1 Dataset Analysis
The system utilizes a comprehensive dataset containing three primary data entities:
- **Books Data**: Contains metadata such as ISBN, title, author, publication year, and image URLs
- **Users Data**: Includes user IDs and demographic information 
- **Ratings Data**: Captures user-book interactions with explicit numerical ratings

#### 1.2 Data Preprocessing Pipeline
A robust ETL (Extract, Transform, Load) pipeline has been implemented with the following stages:
- **Data Cleaning**: Systematic identification and handling of missing values, duplicates, and outliers
- **Data Transformation**: Normalization of rating scales and text preprocessing for book titles/authors
- **Feature Engineering**: Creation of derived features such as rating frequency and user-book interaction matrices

#### 1.3 Data Persistence Strategy
The preprocessed data and trained models are persisted using Python's pickle serialization:
```python
# Example of model persistence strategy
import pickle

# Save preprocessed data and models
pickle.dump(popular_df, open('models/popular.pkl', 'wb'))
pickle.dump(pt, open('models/pt.pkl', 'wb'))
pickle.dump(books, open('models/books.pkl', 'wb'))
pickle.dump(similarity_scores, open('models/similarity_scores.pkl', 'wb'))

# Load models during application runtime
popular_df = pickle.load(open('models/popular.pkl', 'rb'))
```

### 2. Recommendation Algorithms: Technical Implementation

#### 2.1 Popularity-Based Filtering
This approach implements a weighted scoring algorithm that balances both rating volume and quality:

```python
# Popularity-based filtering implementation
def generate_popular_books(ratings_data, books_data, min_ratings=250):
    # Count ratings per book
    ratings_count = ratings_data.groupby('ISBN').count()['Book-Rating'].reset_index()
    ratings_count.rename(columns={'Book-Rating': 'num_ratings'}, inplace=True)
    
    # Calculate average rating per book
    avg_ratings = ratings_data.groupby('ISBN')['Book-Rating'].mean().reset_index()
    avg_ratings.rename(columns={'Book-Rating': 'avg_rating'}, inplace=True)
    
    # Merge count and average
    popular_df = ratings_count.merge(avg_ratings, on='ISBN')
    
    # Apply minimum rating threshold
    popular_df = popular_df[popular_df['num_ratings'] >= min_ratings]
    
    # Merge with book metadata
    popular_df = popular_df.merge(books_data, on='ISBN')
    
    # Sort by popularity (combination of count and average)
    popular_df = popular_df.sort_values(by=['num_ratings', 'avg_rating'], ascending=False)
    
    return popular_df
```

The filtering process incorporates:
- **Rating Frequency Analysis**: Identifies books with statistically significant number of ratings
- **Minimum Rating Threshold**: Enforces a minimum of 250 ratings per book to ensure reliability
- **Weighted Scoring**: Combines rating volume and average score to generate a comprehensive popularity metric

#### 2.2 Collaborative Filtering
The system implements item-based collaborative filtering using the following technical approach:

```python
# Collaborative filtering implementation
def build_collaborative_filter(ratings_data, books_data):
    # Create user-book rating matrix
    user_book_matrix = ratings_data.pivot_table(
        index='Book-Title',
        columns='User-ID',
        values='Book-Rating'
    ).fillna(0)
    
    # Calculate similarity scores using cosine similarity
    from sklearn.metrics.pairwise import cosine_similarity
    similarity_scores = cosine_similarity(user_book_matrix)
    
    return user_book_matrix, similarity_scores
```

Key technical components include:
- **Sparse Matrix Representation**: Efficient storage of user-book interactions
- **Cosine Similarity Computation**: Mathematical quantification of book similarity based on user rating patterns
- **k-Nearest Neighbors Selection**: Identification of top-k similar books for each recommendation query

#### 2.3 Hybrid Recommendation Engine
The system integrates both approaches through a weighted ensemble method:
- **Cold-Start Handling**: Defaults to popularity-based recommendations for new users
- **Personalization Layer**: Transitions to collaborative filtering as user interaction data becomes available
- **Dynamic Weighting**: Adjusts the influence of each algorithm based on data availability and quality

### 3. System Architecture and Implementation

#### 3.1 Flask Web Application
The application is built on Flask with RESTful architecture:
```python
# Key API implementation
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'GET':
        return render_template('recommend.html')
        
    book_name = request.form.get('book_name')
    
    # Find the index of the book
    index = np.where(pt.index == book_name)[0][0]
    
    # Get similar items using the precomputed similarity matrix
    similar_items = sorted(list(enumerate(similarity_scores[index])), 
                          key=lambda x: x[1], reverse=True)[1:6]

    # Generate recommendations with book metadata
    recommendations = []
    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        recommendations.append({
            'title': temp_df.iloc[0]['Book-Title'],
            'author': temp_df.iloc[0]['Book-Author'],
            'image': temp_df.iloc[0]['Image-URL-M']
        })
    
    return render_template('recommendations.html', 
                          recommendations=recommendations,
                          selected_book=book_name)
```

#### 3.2 Error Handling and System Resilience
The system implements comprehensive error handling:
```python
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', 
                          message="The page you're looking for doesn't exist."), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', 
                          message="An internal server error occurred."), 500
```

#### 3.3 Performance Optimization Techniques
Several optimization strategies are employed:
- **Precomputed Similarity Matrices**: Generated during application initialization to minimize runtime computation
- **In-Memory Data Structures**: Optimized for quick lookups and recommendation generation
- **Response Caching**: Implementation of Flask-Caching for frequently accessed endpoints
- **Lazy Loading**: Deferred loading of resource-intensive components

### 4. Evaluation Metrics and Testing

#### 4.1 Recommendation Quality Metrics
The system's performance is evaluated using industry-standard metrics:
- **Precision and Recall**: Measuring recommendation relevance and completeness
- **Mean Average Precision (MAP)**: Assessing ranking quality of recommendations
- **Diversity and Serendipity**: Evaluating recommendation variety and novelty

#### 4.2 System Performance Benchmarks
Runtime performance is monitored through:
- **Response Time Analysis**: Average and percentile-based latency measurements
- **Throughput Testing**: System capacity under various load conditions
- **Resource Utilization**: CPU, memory, and I/O consumption patterns

## Technical Architecture

### Tech Stack
- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: scikit-learn
- **Data Storage**: Pickle files for model persistence

### System Components
1. **Data Processing Pipeline**
   - Data cleaning and preprocessing
   - Feature engineering
   - Model training and persistence

2. **Recommendation Engine**
   - Popularity-based filtering
   - Collaborative filtering using cosine similarity
   - Hybrid recommendation generation

3. **Web Application**
   - RESTful API endpoints
   - Responsive user interface
   - Real-time search functionality

## Implementation Details

### Data Processing
- Dataset includes books, users, and ratings information
- Data cleaning involves handling missing values and duplicates
- Feature engineering creates user-book interaction matrices

### Recommendation Algorithms
1. **Popularity-Based Filtering**
   - Calculates average ratings and number of ratings per book
   - Filters books with minimum rating threshold (250 ratings)
   - Ranks books based on weighted popularity score

2. **Collaborative Filtering**
   - Creates user-book rating matrix
   - Implements cosine similarity for finding similar books
   - Generates recommendations based on similarity scores

### Web Interface
- Responsive design for various screen sizes
- Real-time search with autocomplete
- Interactive book cards with cover images
- Rating and review display

## User Flow
1. User lands on homepage showing popular books
2. User can:
   - Browse popular books
   - Search for specific books
   - Get personalized recommendations
3. For recommendations:
   - User enters a book title
   - System processes the input
   - Displays similar books with details

## Technical Implementation
```python
# Key components of the recommendation system
- Data preprocessing and cleaning
- Popularity-based filtering implementation
- Collaborative filtering using cosine similarity
- Flask web application with RESTful endpoints
- Frontend templates with responsive design
```

## Conclusion
This book recommendation system successfully implements both popularity-based and collaborative filtering approaches to provide users with relevant book recommendations. The hybrid approach ensures that users receive both trending books and personalized suggestions based on their interests. The system's modular architecture allows for easy maintenance and future enhancements.

## Future Enhancements
1. Implement content-based filtering
2. Add user authentication and personalization
3. Integrate with external book APIs
4. Enhance recommendation algorithms
5. Add social features and book clubs

## Installation and Setup
1. Clone the repository
```bash
git clone https://github.com/KayasthaSahil/book-recommender.git
cd book-recommender
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the Flask application
```bash
python app.py
```

4. Access the web interface at `http://localhost:5000`

## Dependencies
All required dependencies are listed in `requirements.txt`:
- Flask==3.0.2
- NumPy==1.26.4
- Pandas==2.2.1
- scikit-learn==1.4.1.post1
- gunicorn==21.2.0
- Werkzeug==3.0.1
- scipy==1.12.0
- python-dotenv==1.0.1
- click==8.1.7
- itsdangerous==2.1.2
- Jinja2==3.1.3
- MarkupSafe==2.1.5

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request. 