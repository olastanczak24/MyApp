###  MyApp
This is a Python-based web application that interacts with a DynamoDB database to manage and display animal images. This app provides a REST API with two main endpoints:

---

### Features
1. **Home Endpoint (`/`)**:
   - Displays the total number of images saved in the database.
   - Lists all the unique types of animals for which images have been saved.

2. **Latest Image Endpoint (`/latest-image`)**:
   - Displays the most recently saved image.
   - Shows details about the image, including its type and timestamp.

---

### Technologies Used
- **Flask**: A lightweight Python web framework to create REST APIs.
- **AWS DynamoDB**: A NoSQL database used to store image metadata.
- **Docker**: For containerizing the application.
- **Python Libraries**:
  - `boto3`: To interact with AWS DynamoDB.
  - `requests`: To fetch images dynamically from URLs.
  - `uuid`: To generate unique IDs for each image.
  - `datetime` and `time`: For timestamping and date handling.

---

### API Endpoints
#### 1. **Home (`/`)**
   - **Method**: `GET`
   - **Description**: Returns information about the total number of images saved in the database and the unique animal types.
   - **Response**:
     ```html
     <h1>Welcome to the Animal Pictures API!</h1>
     <p>Total Images Fetched: [number]</p>
     <p>Animal Types: [list of types]</p>
     ```

#### 2. **Latest Image (`/latest-image`)**
   - **Method**: `GET`
   - **Description**: Displays the most recently saved image along with its type and timestamp.
   - **Response**:
     ```html
     <h1>Latest Image</h1>
     <p>Animal Type: [type]</p>
     <p>Timestamp: [timestamp]</p>
     <img src="[image URL]" alt="Latest Image">
     ```

---

### How It Works
1. **Fetching Images**:
   - Images are fetched dynamically from predefined URLs based on animal types (e.g., dogs, bears, cats).
   - A unique URL is generated for each image request to ensure variety.

2. **Saving to DynamoDB**:
   - Each image is saved to DynamoDB with the following attributes:
     - `AnimalType`: The type of animal (e.g., "dog").
     - `Timestamp`: The time the image was saved, stored in milliseconds.
     - `ImageURL`: The URL of the image.
     - `ImageID`: A unique identifier for the image.

3. **Displaying Data**:
   - The app reads data from DynamoDB to display the number of saved images, their types, and the latest image.

---

### Running Locally

#### 1. Clone the Repository:
```bash
git clone https://github.com/olastanczak24/MyApp.git
cd MyApp
```

#### 2. Set Up Environment Variables:
- Create a `.env` file or export the following variables in your shell:
```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="your-region"
```

#### 3. Install Dependencies:
```bash
pip install -r requirements.txt
```

#### 4. Run the App:
```bash
python app.py
```

#### 5. Access the App:
- Visit `http://127.0.0.1:5000` for the Home page.
- Visit `http://127.0.0.1:5000/latest-image` for the latest saved image.

---

### Running with Docker

#### 1. Build the Docker Image:
```bash
docker build -t myapp .
```

#### 2. Run the Docker Container:
```bash
docker run -d -p 5000:5000 --name flask-app \
  -e AWS_ACCESS_KEY_ID="your-access-key-id" \
  -e AWS_SECRET_ACCESS_KEY="your-secret-access-key" \
  -e AWS_DEFAULT_REGION="your-region" \
  myapp
```

#### 3. Access the App:
- Visit `http://127.0.0.1:5000` for the Home page.
- Visit `http://127.0.0.1:5000/latest-image` for the latest saved image.

#### 4. Check Logs:
```bash
docker logs flask-app
```

#### 5. Stop and Remove the Container:
```bash
docker stop flask-app
docker rm flask-app
```

---