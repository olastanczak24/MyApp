# MyApp

This is an application that fetches images from public APIs, saves them to AWS DynamoDB, and provides a REST API to retrieve the latest saved image. The app also serves a web interface to display the latest image.

## Features
- Fetches images from a URL (e.g., `https://place.dog/200/300`).
- Saves the images to a DynamoDB table with a timestamp and unique ID.
- Provides an API endpoint to retrieve the latest image.
- Displays the latest image in a web interface.

---

## Prerequisites

Before running this application, ensure you have the following:
1. **Python 3.9+** installed on your system.
2. **AWS Account**:
   - Create a DynamoDB table named `AnimalPictures` with the following schema:
     - **Partition Key**: `AnimalType` (String)
     - **Sort Key**: `Timestamp` (String)
3. **Docker** installed if you plan to run the app in a container.

---

## Setting Up

1. Clone the Repository
Clone the repository to your local machine:
```bash
git clone https://github.com/your-username/MyApp.git
cd MyApp
2. Create a .env File
In the root directory of the project, create a .env file and add your AWS credentials:

AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_DEFAULT_REGION=your-region
Replace your-access-key-id, your-secret-access-key, and your-region with your actual AWS credentials and region.

### If you want to run locally
1. Install Dependencies
Create a virtual environment and install the required Python packages:

bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

2. Start the Application
Run the application:
python app.py

3. Access the Application
Open your browser and go to http://localhost:5000 to view the latest image.
Use the API endpoint to retrieve the latest image in JSON format:
bash
curl http://localhost:5000/latest-photo


### Running with Docker
1. Build the Docker Image
Build the Docker image:

bash
docker build -t flask-dynamodb-app:latest .

2. Run the Docker Container
Start the container with your .env file:

bash
docker run -d -p 5000:5000 \
  --env-file .env \
  --name flask-dynamodb-app flask-dynamodb-app:latest

3. Access the Application
Open http://localhost:5000 in your browser.
Retrieve the latest photo JSON:
bash
curl http://localhost:5000/latest-photo

4. Testing the Application
Fetch Images
The app automatically fetches and saves images for the dog and bear animal types to DynamoDB when it starts.

Verify the DynamoDB Table
Check your DynamoDB table (AnimalPictures) to ensure the images are saved.

Access the Latest Image
Open http://localhost:5000 to view the latest image.
Use curl or Postman to test the /latest-photo API.
