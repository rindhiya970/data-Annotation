# Sample YOLO Format Output

## Example 1: Image Annotations

### Input Annotations (from database)
```json
[
  {
    "id": 1,
    "label": "person",
    "x": 100,
    "y": 150,
    "width": 200,
    "height": 300
  },
  {
    "id": 2,
    "label": "car",
    "x": 400,
    "y": 200,
    "width": 150,
    "height": 100
  },
  {
    "id": 3,
    "label": "person",
    "x": 50,
    "y": 300,
    "width": 180,
    "height": 280
  }
]
```

### Image Dimensions
- Width: 1920 pixels
- Height: 1080 pixels

### Output: `image_001.txt`
```
0 0.156250 0.277778 0.104167 0.277778
1 0.289063 0.231481 0.078125 0.092593
0 0.093750 0.407407 0.093750 0.259259
```

### Explanation
```
Line 1: person (class_id=0)
  x_center = (100 + 200/2) / 1920 = 200 / 1920 = 0.156250
  y_center = (150 + 300/2) / 1080 = 300 / 1080 = 0.277778
  width = 200 / 1920 = 0.104167
  height = 300 / 1080 = 0.277778

Line 2: car (class_id=1)
  x_center = (400 + 150/2) / 1920 = 475 / 1920 = 0.289063
  y_center = (200 + 100/2) / 1080 = 250 / 1080 = 0.231481
  width = 150 / 1920 = 0.078125
  height = 100 / 1080 = 0.092593

Line 3: person (class_id=0) - same class_id as first person
  x_center = (50 + 180/2) / 1920 = 140 / 1920 = 0.093750
  y_center = (300 + 280/2) / 1080 = 440 / 1080 = 0.407407
  width = 180 / 1920 = 0.093750
  height = 280 / 1080 = 0.259259
```

---

## Example 2: Video Annotations (ZIP Structure)

### Video Information
- Video ID: 1
- Total Frames: 120
- Annotations: 45 total across various frames

### ZIP Contents: `video_001_yolo.zip`

```
video_001_yolo.zip
├── frame_0001.txt
├── frame_0002.txt
├── frame_0003.txt
├── frame_0004.txt
├── ...
├── frame_0120.txt
└── classes.txt
```

### Sample Frame: `frame_0001.txt`
```
0 0.512345 0.423456 0.234567 0.345678
1 0.678901 0.567890 0.123456 0.234567
```

### Sample Frame: `frame_0002.txt`
```
0 0.498765 0.431234 0.245678 0.356789
1 0.665432 0.554321 0.134567 0.245678
2 0.312345 0.678901 0.098765 0.123456
```

### Sample Frame: `frame_0050.txt` (no annotations)
```
(empty file)
```

### Classes Mapping: `classes.txt`
```
# YOLO Classes Mapping
# Format: class_id label

0 person
1 car
2 dog
```

---

## Example 3: Real-World Scenario

### Scenario: Traffic Monitoring Dataset

#### Image: `traffic_scene_001.jpg`
- Dimensions: 1280x720
- Objects: 3 cars, 2 persons, 1 traffic light

#### Annotations in Database
```json
[
  {"label": "car", "x": 100, "y": 200, "width": 150, "height": 100},
  {"label": "car", "x": 400, "y": 250, "width": 180, "height": 120},
  {"label": "car", "x": 800, "y": 300, "width": 160, "height": 110},
  {"label": "person", "x": 50, "y": 400, "width": 80, "height": 200},
  {"label": "person", "x": 1100, "y": 380, "width": 75, "height": 210},
  {"label": "traffic_light", "x": 600, "y": 50, "width": 40, "height": 100}
]
```

#### Output: `traffic_scene_001.txt`
```
0 0.136719 0.347222 0.117188 0.138889
0 0.382813 0.430556 0.140625 0.166667
0 0.609375 0.486111 0.125000 0.152778
1 0.070313 0.694444 0.062500 0.277778
1 0.878906 0.673611 0.058594 0.291667
2 0.484375 0.138889 0.031250 0.138889
```

#### Classes File: `classes.txt`
```
# YOLO Classes Mapping
# Format: class_id label

0 car
1 person
2 traffic_light
```

---

## Example 4: Edge Cases

### Case 1: Image with No Annotations

**Output: `empty_image.txt`**
```
(empty file - 0 bytes)
```

### Case 2: Bounding Box at Image Edge

**Input:**
- Image: 800x600
- Annotation: `{"label": "object", "x": 750, "y": 550, "width": 50, "height": 50}`

**Output:**
```
0 0.968750 0.958333 0.062500 0.083333
```

**Note:** Values clamped to 0-1 range even if box extends beyond image

### Case 3: Very Small Object

**Input:**
- Image: 1920x1080
- Annotation: `{"label": "small_object", "x": 1000, "y": 500, "width": 10, "height": 15}`

**Output:**
```
0 0.523438 0.467593 0.005208 0.013889
```

### Case 4: Multiple Labels with Special Characters

**Input Labels:**
- "person-walking"
- "car_sedan"
- "traffic light"

**Classes File:**
```
# YOLO Classes Mapping
# Format: class_id label

0 car_sedan
1 person-walking
2 traffic light
```

**Note:** Labels are normalized (lowercase, trimmed) for consistent mapping

---

## Format Validation

### Valid YOLO Line
```
0 0.500000 0.500000 0.200000 0.300000
```
✅ Correct format: `class_id x_center y_center width height`
✅ All values between 0 and 1
✅ Space-separated
✅ 6 decimal places precision

### Invalid Examples

```
0 1.5 0.5 0.2 0.3
```
❌ x_center > 1 (out of range)

```
0 0.5 0.5 -0.2 0.3
```
❌ Negative width

```
person 0.5 0.5 0.2 0.3
```
❌ Label instead of class_id

```
0,0.5,0.5,0.2,0.3
```
❌ Comma-separated instead of space-separated

---

## Using YOLO Output for Training

### Directory Structure for YOLO Training

```
dataset/
├── images/
│   ├── train/
│   │   ├── image_001.jpg
│   │   ├── image_002.jpg
│   │   └── ...
│   └── val/
│       ├── image_101.jpg
│       └── ...
├── labels/
│   ├── train/
│   │   ├── image_001.txt  (YOLO format)
│   │   ├── image_002.txt
│   │   └── ...
│   └── val/
│       ├── image_101.txt
│       └── ...
└── dataset.yaml
```

### dataset.yaml
```yaml
# YOLO Dataset Configuration
path: ./dataset
train: ./images/train
val: ./images/val

# Classes
nc: 3  # number of classes
names: ['car', 'person', 'traffic_light']
```

### Training Command (YOLOv8)
```bash
yolo train data=dataset.yaml model=yolov8n.pt epochs=100 imgsz=640
```

---

## Conversion Verification

### Python Script to Verify YOLO Format

```python
def verify_yolo_format(yolo_file):
    """Verify YOLO format file is valid."""
    with open(yolo_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) != 5:
                print(f"❌ Line {line_num}: Expected 5 values, got {len(parts)}")
                continue
            
            try:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                
                # Validate ranges
                if not (0 <= x_center <= 1):
                    print(f"❌ Line {line_num}: x_center out of range: {x_center}")
                if not (0 <= y_center <= 1):
                    print(f"❌ Line {line_num}: y_center out of range: {y_center}")
                if not (0 <= width <= 1):
                    print(f"❌ Line {line_num}: width out of range: {width}")
                if not (0 <= height <= 1):
                    print(f"❌ Line {line_num}: height out of range: {height}")
                
                print(f"✅ Line {line_num}: Valid")
                
            except ValueError as e:
                print(f"❌ Line {line_num}: Invalid format - {e}")

# Usage
verify_yolo_format('annotations.txt')
```

---

## Summary

- **Format**: `<class_id> <x_center> <y_center> <width> <height>`
- **Normalization**: All coordinates divided by image dimensions
- **Class IDs**: Deterministic mapping from labels
- **Precision**: 6 decimal places
- **Empty Files**: Valid for frames/images without annotations
- **ZIP for Videos**: Contains per-frame .txt files + classes.txt
