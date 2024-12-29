import os
import time
import uuid
import datetime
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

# Fetch pictures from a URL
def fetch_pictures(count):
    url = "https://place.dog/200/300"
    images = []
    for _ in range(count):
        try:
            print(f"Requesting image from URL: {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                images.append(url)
            else:
                print(f"Failed to fetch image: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image: {e}")
    return images

# Save images to DynamoDB
def save_images_to_dynamodb(animal_type, image_urls):
    for image_url in image_urls:
        print(f"Saving image to DynamoDB: {image_url}")
        table.put_item(
            Item={
                'AnimalType': animal_type,
                'Timestamp': str(int(time.time() * 1000)),
                'ImageURL': image_url,
                'ImageID': str(uuid.uuid4()),
            }
        )
    print("All images saved to DynamoDB!")

# Get the last saved photo for specified animal types
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
    # Test saving and fetching
    animal_types = ["dog", "bear"]
    image_urls = fetch_pictures(1)
    save_images_to_dynamodb("dog", image_urls)
    save_images_to_dynamodb("bear", ["https://placebear.com/g/200/300"])

    # Print the last saved photo
    result = get_last_saved_photo(animal_types)
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

