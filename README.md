# 🎾 Slicer Tennis Feedback API
This repository powers the Slicer App, an AI-driven tennis technique analysis platform. Slicer analyzes uploaded videos of forehand or backhand drills, extracts key swing phases, and provides detailed feedback and metrics — all seamlessly integrated with Cloudinary and Airtable.

# Project Structure
├── app.py                  Main Flask API endpoint

├── analyze_video.py        Core analysis logic for forehand and backhand

├── get_frames.py           Video-to-frame extractor (not shown here)

├── connect_airtable.py     # Function to upload results to Airtable (not shown here)

├── fh_algorithms.py        # Forehand-specific feedback algorithms

├── bh_algorithms.py        # Backhand-specific feedback algorithms

├── normalize_points.py     # Normalization for pose keypoints

# Features
- Video Upload & Frame Extraction: Extracts frames from a provided AWS S3 video URL.
- Pose Detection: Identifies critical body landmarks using cvzone.PoseModule.
- Swing Phase Detection:
  - Detects Takeback, Contact Point, and Follow Through for each swing.
- Feedback Generation:
- Classifies movements (e.g. "Looks good!" or errors).
- Calculates technique accuracy, swing speed, and consistency.
- Image Uploads: Annotated frames uploaded to Cloudinary.
- Data Storage: Analysis results pushed to Airtable.

# API Endpoint
POST /slicer/analyze
Analyzes a user-uploaded video.

INPUT JSON 

{
  "ShortDescription": "10 FH",
  "Video": "https://your-s3-link.com/video.mp4",
  "UserID": "user_123",
  "When": "2025-04-21",
  "DrillName": "Baseline Rally"
}

OUTPUT JSON

{
  "fields": {
    "Timestamp": "4/21 3:45pm",
    "UserID": "user_123",
    "DrillName": "Baseline Rally",
    "ShortDescription": "10 FH",
    "TechniqueAccuracy": 88,
    "Consistency": 95,
    "SwingSpeed": 1.73,
    "Restarts": 0,
    "Pics": [{"url": "https://res.cloudinary.com/..."}, ...],
    "When": "2025-04-21"
  }
}

# How it Works (Behind the Scenes)
1. JSON containing the video + context is recieved by the API
2. Frames are extracted from video URL
4. In analyze_video, body position joints are identified and then Takeback, Contact point, Follow through parts of the tennis swing are identified.
5. In fh_algorithms or bh_algorithms, the body position joints are analyzed to extract feedback.
6. Data is sent back to an AirTable database that connects to the frontend


![Screen Shot 2025-04-21 at 12 25 55 PM](https://github.com/user-attachments/assets/0144d00b-9bb1-4e6f-a36d-18885eadc0bf)

