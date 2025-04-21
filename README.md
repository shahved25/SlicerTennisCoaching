# 🎾 Slicer Tennis

This repository powers the **Slicer App**, an AI-driven tennis technique analysis platform. Slicer analyzes uploaded videos of forehand or backhand drills, extracts key swing phases, and provides detailed feedback and metrics.

---

## 📂 Project Structure

```bash
├── api.py                  # Main Flask API endpoint
├── analyze_video.py        # Core analysis logic for forehand and backhand
├── get_frames.py           # Video-to-frame extractor (not shown here)
├── connect_airtable.py     # Function to upload results to Airtable (not shown here)
├── fh_algorithms.py        # Forehand-specific feedback algorithms
├── bh_algorithms.py        # Backhand-specific feedback algorithms
├── normalize_points.py     # Normalization for pose keypoints
```

---

## 🔧 Features

- **Video Upload & Frame Extraction**: Extracts frames from a provided AWS S3 video URL.
- **Pose Detection**: Identifies critical body landmarks using `cvzone.PoseModule`.
- **Swing Phase Detection**:
  - Detects **Takeback**, **Contact Point**, and **Follow Through** for each swing.
- **Feedback Generation**:
  - Classifies movements (e.g. "Looks good!" or errors).
  - Calculates technique accuracy, swing speed, and consistency.
- **Image Uploads**: Annotated frames uploaded to **Cloudinary**.
- **Data Storage**: Analysis results pushed to **Airtable**.

---

## 🔌 API Endpoint

### `POST /slicer/analyze`

Analyzes a user-uploaded video.

#### 📥 Input (JSON)
```json
{
  "ShortDescription": "10 FH",
  "Video": "https://your-s3-link.com/video.mp4",
  "UserID": "user_123",
  "When": "2025-04-21",
  "DrillName": "Baseline Rally"
}
```

#### 📤 Output (JSON)
```json
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
```

---
## 🧠 How it Works (Behind the Scenes)

1. Video is parsed into frames (every 1/30th second).
2. Body keypoints are extracted using `cvzone.PoseModule`.
3. For each swing, the code looks for:
   - **Takeback**: Arm behind body
   - **Contact Point**: Arm extended in front of hip
   - **Follow Through**: Arm across the body or shoulder height
4. Feedback for each phase is generated using posture heuristics from `fh_algorithms.py` or `bh_algorithms.py`.
5. Annotated frames are uploaded to Cloudinary, while stats are logged in Airtable.

---

## 📈 Metrics Tracked

| Metric             | Description |
|--------------------|-------------|
| `TechniqueAccuracy` | % of body parts in correct positions |
| `Consistency`       | Penalized for restart delays |
| `SwingSpeed`        | Frame difference between takeback and follow-through |
| `Restarts`          | How often 3+ seconds passed before resuming swing |

---
