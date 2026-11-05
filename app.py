"""Video Annotation Tool: frame-level bounding boxes and time-segment tags, exported to JSON."""
import json
import os
import tempfile

import cv2
import streamlit as st

from validators import validate_annotations

with open("label_schema.json") as f:
    SCHEMA = json.load(f)
BOX_LABELS = SCHEMA["box_labels"]
EVENT_LABELS = SCHEMA["event_labels"]

st.set_page_config(page_title="Video Annotation Tool", layout="wide")
st.title("Video Annotation Tool")

if "boxes" not in st.session_state:
    st.session_state.boxes = []
    st.session_state.segments = []

uploaded = st.sidebar.file_uploader("Upload a video", type=["mp4", "avi", "mov", "mkv"])
if uploaded is None:
    st.info("Upload a short video (mp4/avi/mov) in the sidebar to begin.")
    st.stop()

# Save once to a temp file so OpenCV can read it
if st.session_state.get("video_name") != uploaded.name:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1])
    tmp.write(uploaded.read())
    tmp.close()
    st.session_state.video_path = tmp.name
    st.session_state.video_name = uploaded.name
    st.session_state.boxes, st.session_state.segments = [], []

cap = cv2.VideoCapture(st.session_state.video_path)
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

frame_no = st.sidebar.slider("Frame", 0, max(total - 1, 0), 0)
st.sidebar.caption(f"{width}x{height} | {total} frames | {fps:.1f} fps | time {frame_no / fps:.2f}s")

cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
ok, frame = cap.read()
cap.release()
if not ok:
    st.error("Could not read this frame.")
    st.stop()

# Draw the boxes that belong to this frame
for b in st.session_state.boxes:
    if b["frame"] == frame_no:
        cv2.rectangle(frame, (b["x1"], b["y1"]), (b["x2"], b["y2"]), (0, 255, 0), 2)
        cv2.putText(frame, b["label"], (b["x1"], max(b["y1"] - 6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

left, right = st.columns([3, 2])
left.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption=f"Frame {frame_no}", use_container_width=True)

with right:
    st.subheader("Add bounding box")
    label = st.selectbox("Label", BOX_LABELS)
    c1, c2 = st.columns(2)
    x1 = c1.number_input("x1", 0, width, 0)
    y1 = c2.number_input("y1", 0, height, 0)
    x2 = c1.number_input("x2", 0, width, min(100, width))
    y2 = c2.number_input("y2", 0, height, min(100, height))
    if st.button("Add box to this frame"):
        st.session_state.boxes.append(
            {"frame": frame_no, "label": label, "x1": int(x1), "y1": int(y1), "x2": int(x2), "y2": int(y2)})
        st.rerun()

    st.subheader("Add time segment")
    event = st.selectbox("Event", EVENT_LABELS)
    s1, s2 = st.columns(2)
    start = s1.number_input("Start frame", 0, max(total - 1, 0), frame_no)
    end = s2.number_input("End frame", 0, max(total - 1, 0), min(frame_no + 30, max(total - 1, 0)))
    if st.button("Add segment"):
        st.session_state.segments.append({"start_frame": int(start), "end_frame": int(end), "label": event})
        st.rerun()

st.divider()
t1, t2 = st.columns(2)
t1.subheader("Boxes")
t1.dataframe(st.session_state.boxes, use_container_width=True)
t2.subheader("Segments")
t2.dataframe(st.session_state.segments, use_container_width=True)

if st.button("Undo last box") and st.session_state.boxes:
    st.session_state.boxes.pop()
    st.rerun()

output = {
    "video": {"name": st.session_state.video_name, "width": width, "height": height,
              "fps": fps, "total_frames": total},
    "boxes": st.session_state.boxes,
    "segments": st.session_state.segments,
}
problems = validate_annotations(output, BOX_LABELS, EVENT_LABELS)
if problems:
    st.warning("Fix these before exporting:")
    for p in problems:
        st.write(f"- {p}")
else:
    st.success("Annotations pass all validation checks.")
    st.download_button("Download annotations (JSON)", json.dumps(output, indent=2),
                       file_name="annotations.json", mime="application/json")
