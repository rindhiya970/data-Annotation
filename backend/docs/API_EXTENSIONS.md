# API Extensions Documentation

## New Features Added

### 1. Image Annotation Support
### 2. Annotated Media Export

---

## 1. IMAGE ANNOTATION ENDPOINTS

### POST /annotations/image

Create annotation on an uploaded image file.

**Authentication**: JWT Required

**Request Body** (JSON):
```json
{
  "file_id": 1,
  "label": "person",
  "x": 100.5,
  "y": 200.3,
  "width": 50.0,
  "height": 80.0
}
```

**Validation Rules**:
- `file_id`: Must exist and belong to authenticated user
- File must be type 'image' (not 'video')
- `label`: Cannot be empty
- `x` >= 0, `y` >= 0
- `width` > 0, `height` > 0

**Success Response** (201):
```json
{
  "message": "Image annotation created successfully",
  "annotation": {
    "id": 1,
    "user_id": 1,
    "file_id": 5,
    "video_id": null,
    "frame_id": null,
    "label": "person",
    "x": 100.5,
    "y": 200.3,
    "width": 50.0,
    "height": 80.0,
    "created_at": "2026-02-14T10:30:00",
    "updated_at": "2026-02-14T10:30:00"
  }
}
```

**Error Responses**:
- 400: Validation errors
- 401: Unauthorized
- 500: Internal server error

**Example (cURL)**:
```bash
curl -X POST http://localhost:5000/annotations/image \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": 1,
    "label": "car",
    "x": 150.0,
    "y": 200.0,
    "width": 100.0,
    "height": 80.0
  }'
```

**Example (Axios)**:
```javascript
const response = await axios.post('/annotations/image', {
  file_id: 1,
  label: 'person',
  x: 100.5,
  y: 200.3,
  width: 50.0,
  height: 80.0
}, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

---

### GET /annotations/image/{file_id}

Get all annotations for a specific image file.

**Authentication**: JWT Required

**URL Parameters**:
- `file_id` (int): ID of the image file

**Success Response** (200):
```json
{
  "file_id": 1,
  "count": 2,
  "annotations": [
    {
      "id": 1,
      "user_id": 1,
      "file_id": 1,
      "video_id": null,
      "frame_id": null,
      "label": "person",
      "x": 100.5,
      "y": 200.3,
      "width": 50.0,
      "height": 80.0,
      "created_at": "2026-02-14T10:30:00",
      "updated_at": "2026-02-14T10:30:00"
    }
  ]
}
```

**Error Responses**:
- 404: File not found or access denied
- 401: Unauthorized
- 500: Internal server error

---

## 2. ANNOTATED MEDIA EXPORT ENDPOINTS

### GET /export/annotated-image/{file_id}

Export image with annotations drawn as bounding boxes.

**Authentication**: JWT Required

**URL Parameters**:
- `file_id` (int): ID of the image file

**Response**: 
- Content-Type: `image/jpeg`
- Content-Disposition: `attachment; filename=original_name_annotated.jpg`
- Binary image data with bounding boxes and labels drawn

**Features**:
- Draws bounding boxes with different colors per label
- Displays label text above each box
- Returns original image if no annotations exist

**Error Responses**:
- 400: Invalid file or processing error
- 404: File not found or access denied
- 401: Unauthorized
- 500: Internal server error

**Example (cURL)**:
```bash
curl -X GET http://localhost:5000/export/annotated-image/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o annotated_image.jpg
```

**Example (Axios - Download)**:
```javascript
const response = await axios.get(`/export/annotated-image/${fileId}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  },
  responseType: 'blob'
});

// Create download link
const url = window.URL.createObjectURL(new Blob([response.data]));
const link = document.createElement('a');
link.href = url;
link.setAttribute('download', 'annotated_image.jpg');
document.body.appendChild(link);
link.click();
link.remove();
```

---

### GET /export/annotated-video/{video_id}

Export video with annotations drawn on frames.

**Authentication**: JWT Required

**URL Parameters**:
- `video_id` (int): ID of the processed video

**Response**:
- Content-Type: `video/mp4`
- Content-Disposition: `attachment; filename=original_name_annotated.mp4`
- Binary video data with annotations on frames

**Features**:
- Maintains original video FPS
- Draws annotations on corresponding frames
- Different colors per label
- Returns original video if no annotations exist

**⚠️ Important Notes**:
- **Long-running operation** (can take several minutes for long videos)
- Frontend should show loading indicator
- Consider implementing timeout handling
- For production, consider async processing with job queue

**Error Responses**:
- 400: Invalid video or processing error
- 404: Video not found or access denied
- 401: Unauthorized
- 500: Internal server error

**Example (cURL)**:
```bash
curl -X GET http://localhost:5000/export/annotated-video/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o annotated_video.mp4
```

**Example (Axios - Download with Progress)**:
```javascript
const response = await axios.get(`/export/annotated-video/${videoId}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  },
  responseType: 'blob',
  timeout: 300000, // 5 minute timeout
  onDownloadProgress: (progressEvent) => {
    const percentCompleted = Math.round(
      (progressEvent.loaded * 100) / progressEvent.total
    );
    console.log(`Download progress: ${percentCompleted}%`);
  }
});

// Trigger download
const url = window.URL.createObjectURL(new Blob([response.data]));
const link = document.createElement('a');
link.href = url;
link.setAttribute('download', 'annotated_video.mp4');
document.body.appendChild(link);
link.click();
link.remove();
```

---

## Database Schema Changes

### Annotations Table Updates

**Modified Columns**:
- `video_id`: Changed from NOT NULL to NULL
- `frame_id`: Changed from NOT NULL to NULL

**New Columns**:
- `file_id`: INT NULL (foreign key to files.id)

**New Constraints**:
- Check constraint: Ensures either `file_id` OR (`frame_id` AND `video_id`) is set
- Foreign key: `file_id` references `files(id)` with CASCADE delete

**Migration SQL**: See `backend/migrations/001_add_image_annotation_support.sql`

---

## Testing Strategy

### Unit Tests
- Test image annotation creation with valid data
- Test validation errors (missing fields, invalid coordinates)
- Test file ownership validation
- Test file type validation (image vs video)

### Integration Tests
- Test complete workflow: upload → annotate → export
- Test annotated image generation
- Test annotated video generation
- Test error handling for missing files

### Manual Testing
1. Upload an image file
2. Create multiple annotations on the image
3. Export annotated image and verify bounding boxes
4. Upload a video and process it
5. Create annotations on video frames
6. Export annotated video and verify annotations appear on correct frames

### Test Script
Run: `python backend/tests/test_image_annotations.py`

---

## Security Considerations

1. **Path Traversal Prevention**: All file paths validated with `os.path.abspath()`
2. **User Authorization**: All endpoints verify file/video ownership
3. **Input Validation**: Coordinates and dimensions validated
4. **File Type Validation**: Ensures images aren't processed as videos and vice versa
5. **Database Constraints**: Check constraint prevents invalid annotation states

---

## Performance Considerations

### Annotated Image Export
- **Fast**: Typically < 1 second
- Memory efficient for standard image sizes

### Annotated Video Export
- **Slow**: Can take 1-5+ minutes depending on video length
- Memory usage scales with video resolution
- **Recommendation**: Implement async processing for production
  - Use Celery or similar task queue
  - Return job ID immediately
  - Poll for completion status
  - Notify user when ready

---

## Backward Compatibility

✅ **All existing endpoints remain unchanged**
✅ **Existing video frame annotations continue to work**
✅ **Database migration is additive (no data loss)**
✅ **Existing API contracts maintained**

---

## Future Enhancements

1. **Async Video Processing**: Implement job queue for long-running exports
2. **Progress Tracking**: WebSocket or polling endpoint for export progress
3. **Batch Export**: Export multiple files at once
4. **Custom Styling**: Allow users to customize annotation colors/styles
5. **Video Streaming**: Stream annotated video instead of full download
6. **Annotation History**: Track annotation changes over time
