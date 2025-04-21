# This is the main Flask API.

from flask import Flask, request, jsonify
from analyze_video import *
from connect_airtable import *
from get_frames import *
import json
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import datetime
from collections import Counter

# Cloudinary Configuration for Image Storage
cloudinary.config(
    cloud_name = "djqozkboz",
    api_key = "146155129725499",
    api_secret = "v2vfZ5Liie_NetZ1yig6IFgCO8I", 
    secure=True
)

app = Flask(__name__)

# Routing for all requests
@app.route('/slicer/analyze', methods=['POST'])
def analyze():
    print('REQUEST ANALYZE')
    # Receive Data
    data = request.json
    shortDescription = data.get('ShortDescription')
    video_url = str(data.get('Video'))
    userid = data.get('UserID')
    when = data.get('When')
    drillName = data.get('DrillName')
    number_of_shots = int(''.join([i for i in shortDescription if i.isdigit()]) or 0)
    type = 'fh' if "FH" in shortDescription else 'bh'
    current_time = datetime.datetime.now()
    hour = current_time.hour - 12 if current_time.hour > 12 else current_time.hour
    ampm = 'pm' if current_time.hour > 12 else 'am'
    minutes = current_time.minute if len(str(current_time.minute)) == 2 else '0' + str(current_time.minute)
    timestamp = f'{current_time.month}/{current_time.day} {hour}:{minutes}{ampm}'
    print(f"{'User ID:':<20}{userid}")
    print(f"{'Drill Name:':<20}{drillName}")
    print(f"{'Short Description:':<20}{shortDescription}")
    print(f"{'Video URL:':<20}{video_url}")
    print(f"{'Number of Shots:':<20}{number_of_shots}")
    print(f"{'Shot Type:':<20}{type}")
    print(f"{'Timestamp:':<20}{timestamp}")

    # Get frames from AWS temporary storage file - THIS WILL NEED TO CHANGE BASED ON WHERE THE IMAGE IS COMING FROM
    if video_url.startswith('https'):
        frameList = handle_aws_file(video_url)
        print(f"{'Number of Frames:':<15}{len(frameList)}")

        # Analyze Frames
        feedback, pics, analysis = analyze_video(frameList, type, number_of_shots)
        print(feedback)
        print(pics)
        # Save results to Airtable
        pics = [{"url": pic} for pic in pics]
        data = {
            "fields": {
                "Timestamp": timestamp,
                "UserID": userid,
                "DrillName": drillName,
                "ShortDescription": shortDescription,
                "TechniqueAccuracy": int(analysis["technique_accuracy"]),
                "Consistency": int(analysis['consistency']),
                "SwingSpeed": float(analysis['swing_speed']),
                "Restarts": int(analysis['restarts']),
                "Pics": pics,
                "When": when
            }
        }
        airtable(data)

    else:
        data = {'error':'video_not_valid'}
    return data, 201

# This is a test request for debugging
@app.route('/slicer/test', methods=['POST', 'GET'])
def test():
    data = request.json

    return {"Test Successful":201}

if __name__ == '__main__':
    print("API Trying")
    # serve(app, host='0.0.0.0', port=5000, channel_timeout=3000)
    app.run(debug=True)
    print("API Started")
