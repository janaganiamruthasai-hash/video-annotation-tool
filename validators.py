"""Validation rules for video annotations. Kept separate from the UI so it can be tested."""

BOX_FIELDS = {"frame", "label", "x1", "y1", "x2", "y2"}
SEGMENT_FIELDS = {"start_frame", "end_frame", "label"}


def validate_annotations(data, allowed_boxes, allowed_events):
    """Return a list of human-readable problems. Empty list means the file is clean."""
    problems = []
    width, height = data["video"]["width"], data["video"]["height"]
    total = data["video"]["total_frames"]

    for i, b in enumerate(data.get("boxes", [])):
        tag = f"Box #{i + 1} (frame {b.get('frame')})"
        if not BOX_FIELDS.issubset(b):
            problems.append(f"{tag}: missing fields")
            continue
        if b["label"] not in allowed_boxes:
            problems.append(f"{tag}: unknown label '{b['label']}'")
        if not (0 <= b["frame"] < total):
            problems.append(f"{tag}: frame outside video")
        if b["x2"] <= b["x1"] or b["y2"] <= b["y1"]:
            problems.append(f"{tag}: empty or inverted box")
        if b["x1"] < 0 or b["y1"] < 0 or b["x2"] > width or b["y2"] > height:
            problems.append(f"{tag}: box outside image bounds")

    segs = data.get("segments", [])
    for i, s in enumerate(segs):
        tag = f"Segment #{i + 1}"
        if not SEGMENT_FIELDS.issubset(s):
            problems.append(f"{tag}: missing fields")
            continue
        if s["label"] not in allowed_events:
            problems.append(f"{tag}: unknown label '{s['label']}'")
        if s["end_frame"] <= s["start_frame"]:
            problems.append(f"{tag}: end must be after start")
        if s["start_frame"] < 0 or s["end_frame"] >= total:
            problems.append(f"{tag}: outside video")

    # overlapping segments with the same label
    by_label = {}
    for s in segs:
        if SEGMENT_FIELDS.issubset(s):
            by_label.setdefault(s["label"], []).append((s["start_frame"], s["end_frame"]))
    for label, spans in by_label.items():
        spans.sort()
        for (a1, a2), (b1, b2) in zip(spans, spans[1:]):
            if b1 < a2:
                problems.append(f"Overlapping '{label}' segments: {a1}-{a2} and {b1}-{b2}")
    return problems
