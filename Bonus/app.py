#!/usr/bin/env python
# coding: utf-8

from flask import Flask, jsonify, request
from flask_ngrok import run_with_ngrok
from pymongo import MongoClient
from bson import ObjectId

# This helper function will format the MongoDB ObjectId so that it can be serialized by JSON
def format_objectid(record):
    # I need to convert ObjectId to string, otherwise it can't be handled by JSON
    record["_id"] = str(record["_id"])
    return record

# Initialize Flask app
app = Flask(__name__)

# I am using ngrok during development to make the API publicly accessible
run_with_ngrok(app)  # ngrok helps expose the app on a public URL during development

# Set the Flask app to debugging mode so I can catch issues easily
app.config['DEBUG'] = True

# MongoDB setup: connecting to the database and collection
client = MongoClient("mongodb+srv://user1:123pass123@cluster0.t7maj.mongodb.net/?retryWrites=true&w=majority")
db = client["earthquake_data_db"]
collection = db["earthquakes"]

# Helper function to format MongoDB ObjectId
def format_objectid(earthquake):
    # I need to convert MongoDB's _id to string so it's JSON serializable
    earthquake["_id"] = str(earthquake["_id"])
    return earthquake

# This is my API endpoint to get all earthquake records
@app.route('/api/earthquakes', methods=['GET'])
def get_all_earthquakes():
    # I fetch all earthquakes from the database
    earthquakes = list(collection.find())
    
    # Then I format them to ensure they are JSON serializable
    formatted_earthquakes = [format_objectid(earthquake) for earthquake in earthquakes]
    
    # Returning the earthquakes as a JSON response
    return jsonify(formatted_earthquakes)

# This is the endpoint to get a specific earthquake by its ID
@app.route('/api/earthquakes/<earthquake_id>', methods=['GET'])
def get_earthquake_by_id(earthquake_id):
    try:
        print(f"Fetching earthquake data for ID: {earthquake_id}")
        # I search for the earthquake in the database using the 'id' field
        earthquake = collection.find_one({"id": earthquake_id})
        
        if earthquake:
            print(f"Found earthquake: {earthquake}")
            # I format the earthquake data so it can be returned as JSON
            formatted_earthquake = format_objectid(earthquake)
            return jsonify(formatted_earthquake)
        else:
            print("Earthquake not found")
            return jsonify({"error": "Earthquake not found"}), 404
    except Exception as e:
        print(f"Error retrieving earthquake by id {earthquake_id}: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

# This endpoint lets me filter earthquakes by a date range
@app.route('/api/earthquakes/date-range', methods=['GET'])
def get_earthquakes_by_date_range():
    # I get the start and end dates from the query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # I check if both start and end dates are provided
    if not start_date or not end_date:
        return jsonify({"error": "Please provide both start_date and end_date"}), 400

    # I try to convert the dates to integers (they should be Unix timestamps)
    try:
        start_date = int(start_date)
        end_date = int(end_date)
    except ValueError:
        return jsonify({"error": "Invalid date format. Please provide Unix timestamps."}), 400

    # I query the database for earthquakes within the given date range
    earthquakes = collection.find({
        "properties.time": {"$gte": start_date, "$lte": end_date}
    })

    # I format the earthquakes so they are returned as JSON
    formatted_earthquakes = [format_objectid(earthquake) for earthquake in earthquakes]
    return jsonify(formatted_earthquakes)

# I make sure that the app only runs if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
