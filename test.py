# create_placeholder_images.py
from PIL import Image, ImageDraw
import os

def create_placeholder_image(width, height, text, filename):
    """Create a placeholder image with text"""
    img = Image.new('RGB', (width, height), color='#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # You'd need to calculate text position, but for now just save empty images
    img.save(filename)
    print(f"Created: {filename}")

# Create directories
os.makedirs('static/img/categories', exist_ok=True)
os.makedirs('static/img/product', exist_ok=True)

# Create placeholder images
placeholders = [
    ('static/img/categories/electronics.jpg', 400, 300),
    ('static/img/categories/smartphones.jpg', 400, 300),
    ('static/img/categories/laptops.jpg', 400, 300),
    ('static/img/categories/fashion.jpg', 400, 300),
    ('static/img/categories/mens-fashion.jpg', 400, 300),
    ('static/img/product/iphone14-pro.jpg', 300, 300),
    ('static/img/product/galaxy-s23.jpg', 300, 300),
    ('static/img/product/macbook-air.jpg', 300, 300),
    ('static/img/product/nike-airmax.jpg', 300, 300),
    ('static/img/product/bata-shoes.jpg', 300, 300),
    ('static/img/categories/placeholder.jpg', 400, 300),
    ('static/img/product/placeholder.jpg', 300, 300),
]

for filename, width, height in placeholders:
    create_placeholder_image(width, height, 'Placeholder', filename)
