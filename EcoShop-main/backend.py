from pymongo import MongoClient
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
import numpy as np
import base64
import io
from bson import ObjectId  # To handle MongoDB ObjectId

# Dclass names are in the same order as during training
class_names = ['organic', 'recycle']

# Load the trained model
model_path = 'model_small.h5'
model = load_model(model_path)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017')
db = client['ecommerce_db']  # database name
collection = db['products']

# Image preprocessing parameters (ensure these match your model's input size)
IMG_WIDTH = 80
IMG_HEIGHT = 45

def preprocess_image(img: Image.Image, img_width: int, img_height: int):
    """
    Preprocess the image for model prediction.
    
    Args:
        img (Image.Image): PIL Image.
        img_width (int): Width to resize.
        img_height (int): Height to resize.
    
    Returns:
        np.ndarray: Preprocessed image array.
    """
    img = img.resize((img_width, img_height))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # Normalize to [0,1]
    return img_array

def predict_image(img_array):
    """
    Predict the class of the image.
    
    Args:
        img_array (np.ndarray): Preprocessed image array.
    
    Returns:
        str: Predicted class name.
    """
    prediction = model.predict(img_array)
    predicted_class_index = np.argmax(prediction)
    predicted_class = class_names[predicted_class_index]
    return predicted_class

def update_product_category(product_id, category):
    """
    Update the product category in MongoDB.
    
    Args:
        product_id (ObjectId): The MongoDB ObjectId of the product.
        category (str): The predicted category.
    """
    result = collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"category": category}}
    )
    if result.modified_count > 0:
        print(f"Product ID {product_id} updated with category '{category}'")
    else:
        print(f"Product ID {product_id} not updated or already has category '{category}'")

def process_and_update_products():
    """
    Retrieve products from MongoDB, process images, and update categories.
    """
    # Fetch all products that have an image and category is default or undefined
    query = {
        "image": {"$exists": True, "$ne": None},
        "category": {"$in": ["under processing category"]}  # Adjust based on your default category
    }
    products = collection.find(query)
    
    for product in products:
        product_id = product['_id']
        try:
            # Decode the base64 image
            img_data = base64.b64decode(product['image'])
            img = Image.open(io.BytesIO(img_data))
            img = img.convert("RGB")
    
            # Preprocess the image and make a prediction
            img_array = preprocess_image(img, IMG_WIDTH, IMG_HEIGHT)
            predicted_class = predict_image(img_array)
            
            # Update MongoDB with the predicted category
            update_product_category(product_id, predicted_class)
    
        except Exception as e:
            print(f"Error processing product ID {product_id}: {e}")

if __name__ == '__main__':
    process_and_update_products()
