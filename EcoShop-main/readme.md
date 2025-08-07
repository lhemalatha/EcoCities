

# EcoShop: A Sustainable E-Commerce Platform

## Overview

EcoShop is a web-based sustainable e-commerce platform that promotes eco-friendly products, community-driven initiatives, and the principles of the Circular Economy. The platform allows users to register, log in, buy and sell eco-friendly products, and engage in sustainability-focused community events. It also integrates AI-driven recycling ideas and image classification to categorize products accurately.

## Features

- **User Authentication**: Registration, login, and logout functionalities with secure password handling.
- **Product Management**: Users can upload, edit, and delete eco-friendly products. Products include categories such as "organic" and "recycle".
- **AI Chat**: Users can get AI-generated recycling ideas based on their inputs.
- **Community Engagement**: Users can post and manage sustainability-focused community events.
- **Image Classification**: Uses a pre-trained machine learning model to classify and categorize products based on images.
- **MongoDB Database**: All data is stored in MongoDB, including user accounts, products, and community posts.

## Technologies Used

- **Backend**: Python, Flask
- **Database**: MongoDB
- **Image Processing**: PIL, TensorFlow, Keras
- **Security**: Flask-Bcrypt for password hashing
- **AI**: Custom-trained model for product image classification
- **Web Templates**: Jinja2 for rendering dynamic HTML pages
- **Frontend**: HTML, CSS (Templated in Flask)

## Requirements

To run this project locally, you need the following installed:

- Python 3.x
- MongoDB (running locally on port 27017)
- TensorFlow
- Flask
- Flask-Bcrypt
- Pillow
- pymongo
- numpy
- Keras
- Transformers

You can install the dependencies using `pip`:

```bash
pip install flask flask-bcrypt pymongo tensorflow pillow numpy keras
```

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/harichselvamc/EcoShop.git
   cd EcoShop
   ```

2. **Start MongoDB**:
   Ensure you have MongoDB installed and running on your local machine. If you haven't installed MongoDB, follow the [MongoDB installation guide](https://docs.mongodb.com/manual/installation/).

3. **Run the Flask Application**:
   Start the Flask app by running:

   ```bash
   python app.py
   ```

   The app will be hosted at `http://127.0.0.1:5000/` in your browser.

4. **Upload Product Images**:
   When uploading products, ensure that you follow the correct format (images should be in `.jpg`, `.jpeg`, `.png`, or `.gif` formats).

## Features in Detail

### 1. **Home Page**:
   - Displays featured products along with their details (name, price, description, etc.).
   - Users can navigate to product pages, community posts, or use the AI chat.

### 2. **User Registration & Login**:
   - Secure authentication with password hashing (Flask-Bcrypt).
   - Users can register, log in, and view personalized product listings.

### 3. **Product Management**:
   - Users can add new products with details such as name, price, description, quantity, weight, and image.
   - Products are categorized into "organic", "recycle", etc., either manually or through an AI-based classification.
   - Product images are processed and categorized based on a pre-trained machine learning model.

### 4. **AI Chat (Qwen/Qwen2.5-0.5B)**:
   - Provides a real-time chat interface where users can ask for recycling tips and suggestions.
   - The backend uses the `generate_recycling_idea` function to provide dynamic responses.

### 5. **Community Posts**:
   - Users can create community posts for sustainability-related events or initiatives.
   - Posts support images and allow for contact information, event details, and more.

### 6. **Image Classification for Products**:
   - Products are classified using a TensorFlow model trained to identify categories like "organic" or "recycle" based on the product images.

### 7. **Admin-Style Permissions**:
   - Users can only edit or delete products and posts that they have created.
   
## Folder Structure

```
EcoShop/
│
├── app.py                # Main Flask application
├── backend.py            # Backend utility functions (e.g., AI-related code)
├── llmbackend.py         # AI chat-related functions
├── static/               # Static files (CSS, images, etc.)
│   ├── css/
│   └── images/
├── templates/            # HTML Templates
│   ├── home.html
│   ├── register.html
│   ├── login.html
│   ├── products.html
│   ├── community.html
│   ├── ai_chat.html
│   └── ...
├── model_small.h5        # Pre-trained image classification model
└── requirements.txt      # List of dependencies
```

## MongoDB Collections

- **users**: Stores user information (username, email, password).
- **products**: Stores information about the eco-friendly products (name, description, price, image, etc.).
- **community_posts**: Stores community-driven posts related to sustainability events.
- **purchases**: Stores information about user purchases.

## AI Model

The project uses a TensorFlow-based model (`model_small.h5`) that classifies product images into categories like "organic" or "recycle". The model is trained using a dataset of images that represent different eco-friendly product types.

### Model Details:
- **Model Type**: CNN (Convolutional Neural Network)
- **Input Size**: 80x45 pixels
- **Class Names**: 'organic', 'recycle'

The model is used to process uploaded product images, predict the category, and update the product's category in the database.
