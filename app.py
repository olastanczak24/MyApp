import os
import time
import uuid
import datetime
import random
import json
import boto3
import requests
from flask import Flask, request, jsonify

# AWS DynamoDB Setup
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)
table = dynamodb.Table('AnimalPictures')  # Replace with your table name

app = Flask(__name__)

# Fetch images from a URL
def fetch_pictures(url, count):
    images = []
    for _ in range(count):
        unique_url = f"{url}?random={random.randint(1, 10000)}"
        try:
            response = requests.get(unique_url, timeout=5)
            if response.status_code == 200:
                images.append(unique_url)
        except requests.exceptions.RequestException:
            pass
    return images

# Save images to DynamoDB
def save_images_to_dynamodb(animal_type, image_urls):
    for image_url in image_urls:
        timestamp = str(int(time.time() * 1000))
        table.put_item(
            Item={
                'AnimalType': animal_type,
                'Timestamp': timestamp,
                'ImageURL': image_url,
                'ImageID': str(uuid.uuid4()),
            }
        )

# Fetch all image data from DynamoDB
def fetch_all_images():
    try:
        response = table.scan()
        return response.get('Items', [])
    except Exception:
        return []

# Home Page: Display total images and types
@app.route('/')
def home():
    try:
        images = fetch_all_images()
        if not images:
            return "<h1>No images found</h1>"

        # Calculate stats
        image_count = len(images)
        types = {item['AnimalType'] for item in images}

        # Render stats
        return f"""
        <h1>Welcome to the Animal Pictures API!</h1>
        <p>Total Images Fetched: {image_count}</p>
        <p>Animal Types: {', '.join(types)}</p>
        """
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

# Latest Image Data: Return latest image details as JSON
@app.route('/latest-photo', methods=['GET'])
def latest_photo():
    try:
        images = fetch_all_images()
        if not images:
            return jsonify({"error": "No images found"}), 404

        # Find the latest image
        latest_item = max(images, key=lambda x: int(x['Timestamp']))
        return jsonify({
            "AnimalType": latest_item['AnimalType'],
            "ImageURL": latest_item['ImageURL'],
            "RawTimestamp": latest_item['Timestamp'],
            "ReadableTimestamp": datetime.datetime.fromtimestamp(
                int(latest_item['Timestamp']) / 1000
            ).isoformat(),
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Latest Image Page: Display the last saved image
@app.route('/latest-image', methods=['GET'])
def latest_image():
    try:
        images = fetch_all_images()
        if not images:
            return "<h1>No images found</h1>"

        # Find the latest image
        latest_item = max(images, key=lambda x: int(x['Timestamp']))
        return f"""
        <h1>Latest Image</h1>
        <p>Animal Type: {latest_item['AnimalType']}</p>
        <p>Timestamp: {latest_item['Timestamp']}</p>
        <img src="{latest_item['ImageURL']}" alt="Latest Image" style="max-width: 100%; height: auto;">
        """
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

if __name__ == '__main__':
    # URLs for animal images
    image_urls = {
        "dog": "https://place.dog/200/300",
        "bear": "https://placebear.com/200/300",
        "cat": "https://cataas.com/cat"
    }

    # Fetch and save images
    for animal_type, url in image_urls.items():
        fetched_images = fetch_pictures(url, 1)
        save_images_to_dynamodb(animal_type, fetched_images)

    app.run(host='0.0.0.0', port=5000)


