from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Sample product data for demonstration
sample_products = [
    {
        'id': 1,
        'name': 'Eco-Friendly Water Bottle',
        'price': 25.99,
        'description': 'Sustainable stainless steel water bottle',
        'image': 'bottle.jpg',
        'category': 'Drinkware'
    },
    {
        'id': 2,
        'name': 'Organic Cotton T-Shirt',
        'price': 35.00,
        'description': 'Comfortable organic cotton t-shirt',
        'image': 'tshirt.jpg',
        'category': 'Clothing'
    },
    {
        'id': 3,
        'name': 'Bamboo Phone Case',
        'price': 18.50,
        'description': 'Eco-friendly bamboo phone case',
        'image': 'phonecase.jpg',
        'category': 'Accessories'
    },
    {
        'id': 4,
        'name': 'Solar Power Bank',
        'price': 45.00,
        'description': 'Portable solar-powered charging device',
        'image': 'powerbank.jpg',
        'category': 'Electronics'
    }
]

@app.route('/')
def home():
    try:
        return render_template('index.html', products=sample_products)
    except:
        return '''
        <html>
        <head><title>EcoShop - Sustainable Products</title></head>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h1 style="color: #2e7d32;">🌱 EcoShop - Sustainable Products</h1>
            <p>Welcome to EcoShop! Your one-stop destination for eco-friendly products.</p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px;">
                <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
                    <h3>Eco-Friendly Water Bottle</h3>
                    <p>Sustainable stainless steel water bottle</p>
                    <p><strong>$25.99</strong></p>
                </div>
                <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
                    <h3>Organic Cotton T-Shirt</h3>
                    <p>Comfortable organic cotton t-shirt</p>
                    <p><strong>$35.00</strong></p>
                </div>
                <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
                    <h3>Bamboo Phone Case</h3>
                    <p>Eco-friendly bamboo phone case</p>
                    <p><strong>$18.50</strong></p>
                </div>
                <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
                    <h3>Solar Power Bank</h3>
                    <p>Portable solar-powered charging device</p>
                    <p><strong>$45.00</strong></p>
                </div>
            </div>
            <div style="margin-top: 40px;">
                <h2>Features:</h2>
                <ul>
                    <li>🌿 Eco-friendly products</li>
                    <li>🚚 Fast shipping</li>
                    <li>♻️ Sustainable packaging</li>
                    <li>💚 Supporting green initiatives</li>
                </ul>
            </div>
        </body>
        </html>
        '''

@app.route('/products')
def products():
    return jsonify(sample_products)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    filtered_products = [p for p in sample_products if query in p['name'].lower() or query in p['description'].lower()]
    return jsonify(filtered_products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in sample_products if p['id'] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({'error': 'Product not found'}), 404

if __name__ == '__main__':
    print("🌱 Starting EcoShop website...")
    print("🌐 Website will be available at: http://localhost:5000")
    print("📱 Access your EcoShop website in the browser!")
    app.run(debug=True, host='0.0.0.0', port=5000)
