from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np

client = MongoClient('mongodb://localhost:27017')
db = client['ecommerce_db']
products_collection = db['products']

def get_product_recommendations(product_id, top_n=5):
    products = list(products_collection.find())
    if not products:
        return []

    df = pd.DataFrame(products)
    df['_id'] = df['_id'].astype(str)

    if product_id not in df['_id'].values:
        return []

    # Fill missing values
    for field in ['name', 'description', 'category', 'place', 'owner_name', 'owner_email']:
        df[field] = df.get(field, '').fillna('').astype(str).str.lower()

    # Combine textual fields
    df['combined_text'] = df['name'] + ' ' + df['description'] + ' ' + df['category'] + ' ' + df['place'] + ' ' + df['owner_name'] + ' ' + df['owner_email']

    # Vectorize text
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['combined_text'])

    # Normalize numeric features
    df['price'] = df.get('price', 0).fillna(0).astype(float)
    df['weight'] = df.get('weight', 0).fillna(0).astype(float)
    df['quantity'] = df.get('quantity', 0).fillna(0).astype(int)

    scaler = MinMaxScaler()
    numeric_features = scaler.fit_transform(df[['price', 'weight', 'quantity']])
    
    # Combine text similarity and numeric similarity
    idx = df.index[df['_id'] == product_id].tolist()[0]

    text_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    num_sim = cosine_similarity([numeric_features[idx]], numeric_features).flatten()

    # Weight both similarities
    combined_sim = 0.7 * text_sim + 0.3 * num_sim

    # Get top N similar products (excluding itself)
    sim_scores = list(enumerate(combined_sim))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = [s for s in sim_scores if s[0] != idx][:top_n]

    recommended_indices = [i[0] for i in sim_scores]
    return df.iloc[recommended_indices].to_dict(orient='records')
