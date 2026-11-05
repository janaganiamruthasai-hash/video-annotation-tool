# Video Annotation Tool

A small Streamlit app for annotating video: step through frames, add labeled bounding boxes, tag time segments (events), validate the work, and export everything to JSON.

Built to practice the workflow used in real video annotation projects: follow a label schema, keep annotations consistent, and catch mistakes before submitting.

## Features
- Upload mp4 / avi / mov / mkv and scrub frame by frame
- Bounding boxes with class labels, drawn live on the frame
- Time-segment tags (e.g. walking, idle) by start and end frame
- Label schema in `label_schema.json` (edit it to change the allowed labels)
- Automatic validation: unknown labels, empty or inverted boxes, boxes outside the image, segments outside the video, overlapping segments with the same label
- One-click JSON export (only when validation passes)
- Unit tests for the validation rules

## Run it
```bash
pip install -r requirements.txt
streamlit run app.py
pytest
```

## Output format
```json
{
  "video": {"name": "clip.mp4", "width": 640, "height": 480, "fps": 25.0, "total_frames": 300},
  "boxes": [{"frame": 12, "label": "person", "x1": 100, "y1": 80, "x2": 220, "y2": 300}],
  "segments": [{"start_frame": 0, "end_frame": 60, "label": "walking"}]
}
```

## Possible next steps
- Click-and-drag box drawing with a canvas component
- Box tracking between frames
- Import existing annotations to review and correct them
