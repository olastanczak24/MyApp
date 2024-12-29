import os
import time
import uuid
import datetime
import random
import json
import boto3
import requests
from flask import Flask, jsonify

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

# Function to fetch pictures
def fetch_pictures(url, count):
    images = []
    for _ in range(count):
        # Add a random query parameter to ensure unique fetches
        unique_url = f"{url}?random={random.randint(1, 10000)}"
        try:
            print(f"Requesting image from URL: {unique_url}")
            response = requests.get(unique_url, timeout=5)
            if response.status_code == 200:
                images.append(unique_url)
            else:
                print(f"Failed to fetch image: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image: {e}")
    return images

# Function to save images to DynamoDB
def save_images_to_dynamodb(animal_type, image_urls):
    for image_url in image_urls:
        timestamp = str(int(time.time() * 1000))  # Current time in milliseconds
        print(f"Saving image to DynamoDB: {image_url} with timestamp {timestamp}")
        table.put_item(
            Item={
                'AnimalType': animal_type,
                'Timestamp': timestamp,
                'ImageURL': image_url,
                'ImageID': str(uuid.uuid4()),
            }
        )
    print("All images saved to DynamoDB!")

# Function to get the last saved photo
def get_last_saved_photo(animal_types):
    try:
        latest_photo = None
        latest_timestamp = None

        for animal_type in animal_types:
            # Query DynamoDB for the last saved photo of this animal type
            response = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('AnimalType').eq(animal_type),
                ScanIndexForward=False,  # Get the most recent item
                Limit=1
            )

            if response.get('Items'):
                last_picture = response['Items'][0]
                raw_timestamp = last_picture.get('Timestamp')  # Safely retrieve the Timestamp field

                if not raw_timestamp:
                    print(f"Warning: Missing Timestamp for {animal_type}")
                    continue

                try:
                    raw_timestamp = int(raw_timestamp)  # Convert to integer
                except ValueError:
                    print(f"Warning: Invalid Timestamp format for {animal_type}")
                    continue

                readable_timestamp = datetime.datetime.fromtimestamp(raw_timestamp / 1000).isoformat()

                # Check if this is the latest across all animal types
                if latest_timestamp is None or raw_timestamp > latest_timestamp:
                    latest_photo = {
                        "AnimalType": animal_type,
                        "RawTimestamp": raw_timestamp,
                        "ReadableTimestamp": readable_timestamp,
                        "ImageURL": last_picture['ImageURL']
                    }
                    latest_timestamp = raw_timestamp

        if latest_photo:
            return latest_photo
        else:
            return {"error": "No valid photos found for the given animal types"}
    except Exception as e:
        return {"error": str(e)}

# Manage the save order persistently
def get_save_order():
    order_file = "/app/save_order.json"
    if os.path.exists(order_file):
        with open(order_file, "r") as f:
            data = json.load(f)
            return data.get("order", ["dog", "bear"])
    else:
        return ["dog", "bear"]

def update_save_order(order):
    order_file = "/app/save_order.json"
    new_order = order[::-1]  # Reverse the order for the next run
    with open(order_file, "w") as f:
        json.dump({"order": new_order}, f)
    return new_order

@app.route('/')
def home():
    try:
        response = table.scan()
        if 'Items' not in response or len(response['Items']) == 0:
            return "<h1>No images found in DynamoDB</h1>"

        latest_item = max(response['Items'], key=lambda x: int(x['Timestamp']))
        return f"""
        <h1>Latest Image</h1>
        <p>Timestamp: {latest_item.get('Timestamp')}</p>
        <img src="{latest_item.get('ImageURL')}" alt="Latest Image" style="max-width: 100%; height: auto;">
        """
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

@app.route('/latest-photo', methods=['GET'])
def latest_photo():
    try:
        # Query DynamoDB for all items
        response = table.scan()
        if 'Items' not in response or len(response['Items']) == 0:
            return jsonify({"error": "No images found in DynamoDB"}), 404

        # Find the latest photo by Timestamp
        latest_item = max(response['Items'], key=lambda x: int(x['Timestamp']))

        return jsonify({
            "AnimalType": latest_item.get('AnimalType'),
            "ImageURL": latest_item.get('ImageURL'),
            "RawTimestamp": latest_item.get('Timestamp'),
            "ReadableTimestamp": datetime.datetime.fromtimestamp(
                int(latest_item['Timestamp']) / 1000
            ).isoformat()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # URLs for animal images
    image_urls = {
        "dog": "https://place.dog/200/300",
        "bear": "https://placebear.com/200/300",
    }

    # Determine the save order
    save_order = get_save_order()

    # Fetch and save images based on the current order
    for animal_type in save_order:
        print(f"Fetching image for: {animal_type}")
        fetched_images = fetch_pictures(image_urls[animal_type], 1)
        save_images_to_dynamodb(animal_type, fetched_images)

    # Update the save order for the next restart
    update_save_order(save_order)

    # Print the last saved photo
    result = get_last_saved_photo(["dog", "bear"])
    if "error" not in result:
        print("Last saved photo details:")
        print(f"Animal Type: {result['AnimalType']}")
        print(f"Raw Timestamp: {result['RawTimestamp']}")
        print(f"Readable Timestamp: {result['ReadableTimestamp']}")
        print(f"Image URL: {result['ImageURL']}")
    else:
        print(result["error"])

    # Start the Flask app
    app.run(host='0.0.0.0', port=5000)
