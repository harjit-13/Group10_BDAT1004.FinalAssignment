import requests
import pandas as pd
from pymongo import MongoClient

# MongoDB Connection URI
MONGO_URI = "mongodb+srv://user1:123pass123@cluster0.t7maj.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "earthquake_data_db"
COLLECTION_NAME = "earthquakes"

def get_mongo_connection():
    """Establish a MongoDB connection."""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]

def fetch_and_store_earthquake_data():
    """Fetch earthquake data from the USGS API and store it in MongoDB."""
    endpoint = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        'format': 'geojson',
        'starttime': '2020-01-01',
        'endtime': '2024-12-01',
        'minmagnitude': 5,
        'maxlatitude': 70.67088,
        'minlatitude': -17.81146,
        'maxlongitude': -55.72266,
        'minlongitude': -134.29688
    }

    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        features = data['features']
        df = pd.json_normalize(features)

        # Connect to MongoDB
        collection = get_mongo_connection()
        # Insert data into MongoDB
        records = df.to_dict(orient="records")
        collection.insert_many(records)
        return df
    else:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}")

def get_earthquake_data():
    """Retrieve earthquake data from MongoDB."""
    collection = get_mongo_connection()
    data = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB `_id` field
    return pd.DataFrame(data)
