from flask import Flask, request, jsonify
# from analyze_video import *
from connect_airtable import *
from get_frames import *

import json

app = Flask(__name__)

@app.route('/slicer/analyze_backhand', methods=['POST'])
def analyze_backhand():
    print('REQUEST ANALYZE')
    data = request.json
    # Find info
    shortDescription = data.get('ShortDescription')
    video_url = data.get('Video')
    print("VIDEO:")
    print(video_url)
    drillName = data.get('DrillName')
    number_of_shots = ""
    for i in shortDescription:
        if i in '1234567890':
            number_of_shots += i
        else:
            break
    if number_of_shots:
        number_of_shots = int(number_of_shots)
    if "FH" in shortDescription:
        type = 'fh'
    else:
        type = 'bh'

    print(shortDescription, video_url, drillName, number_of_shots, type)

    # Get frames from AWS temporary storage file
    frameList = handle_aws_file(video_url)

    # Analyze Frames
    feedback = analyze_video(frameList, type, number_of_shots)
    print(feedback)

    data = {
        "fields": {
            "UserID": "Testing",
            "DrillName": drillName,
            "Done": 'True',
            "ShortDescription": shortDescription,
            "TechniqueAccuracy": str(feedback["technique_accuracy"]),
            "Consistency": str(feedback['consistency']),
            "SwingSpeed": str(feedback['swing_speed']),
            "Restarts": str(feedback['restarts'])

        }
    }
    airtable(data)

    return data, 201

@app.route('/slicer/analyze_forehand', methods=['POST'])
def analyze_forehand():
    data = request.json
    # feedback = analyze_video(data['video'], data['type'], data['number_of_shots'])
    # print(json.dumps(
    #     feedback,
    #     sort_keys=True,
    #     indent=4,
    #     separators=(',', ': ')
    # ))
    #print(jsonify(feedback))
    #return jsonify(feedback), 201
    # return feedback, 201

if __name__ == '__main__':
    print("API Trying")
    # serve(app, host='0.0.0.0', port=5000, channel_timeout=3000)
    app.run(debug=True)
    print("API Started")
