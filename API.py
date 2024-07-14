from flask import Flask, request, jsonify
from analyze_video import *
from pyngrok import ngrok
from waitress import serve

import json

app = Flask(__name__)

@app.route('/slicer/analyze_backhand', methods=['GET'])
def analyze_backhand():
    print('REQUEST ANALYZE BACKHAND')
    #feedback = request.args.get('video')
    data = request.args.to_dict()
    print(data)
    feedback = data['video']
    analysis = {
        'technique_accuracy': 0, 
        'consistency': 0,
        'swing_speed': 0,
        'restarts': 0,
        'number_of_frames': feedback,
        'video': 'feedback2'
    }
    #print(feedback)
    #print(feedback2)
    return analysis, 201

@app.route('/slicer/analyze_forehand', methods=['POST'])
def analyze_forehand():
    data = request.json
    feedback = analyze_video(data['video'], data['type'], data['number_of_shots'])
    # print(json.dumps(
    #     feedback,
    #     sort_keys=True,
    #     indent=4,
    #     separators=(',', ': ')
    # ))
    #print(jsonify(feedback))
    #return jsonify(feedback), 201
    return feedback, 201

if __name__ == '__main__':
    # Set up ngrok
    port = 5000
    #public_url = ngrok.connect(port)
    #print(f" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{port}\"")

    # Run app with waitress on port 5000
    serve(app, host='0.0.0.0', port=5000, channel_timeout=300)
