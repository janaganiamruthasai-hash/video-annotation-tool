from validators import validate_annotations

BOXES = ["person", "car"]
EVENTS = ["walking", "idle"]
BASE = {"video": {"width": 640, "height": 480, "total_frames": 100}}


def make(boxes=None, segments=None):
    return {**BASE, "boxes": boxes or [], "segments": segments or []}


def test_clean_file_has_no_problems():
    d = make([{"frame": 1, "label": "person", "x1": 10, "y1": 10, "x2": 50, "y2": 80}],
             [{"start_frame": 0, "end_frame": 20, "label": "walking"}])
    assert validate_annotations(d, BOXES, EVENTS) == []


def test_inverted_box_and_unknown_label():
    d = make([{"frame": 1, "label": "cat", "x1": 50, "y1": 10, "x2": 10, "y2": 80}])
    probs = validate_annotations(d, BOXES, EVENTS)
    assert any("unknown label" in p for p in probs)
    assert any("empty or inverted" in p for p in probs)


def test_box_out_of_bounds():
    d = make([{"frame": 1, "label": "car", "x1": 0, "y1": 0, "x2": 700, "y2": 80}])
    assert any("outside image" in p for p in validate_annotations(d, BOXES, EVENTS))


def test_overlapping_segments():
    d = make(segments=[{"start_frame": 0, "end_frame": 30, "label": "walking"},
                       {"start_frame": 20, "end_frame": 50, "label": "walking"}])
    assert any("Overlapping" in p for p in validate_annotations(d, BOXES, EVENTS))
