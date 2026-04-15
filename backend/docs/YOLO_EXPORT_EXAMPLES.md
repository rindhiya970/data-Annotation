# YOLO Format Export - API Examples

## Overview

The YOLO export feature converts bounding box annotations to YOLO format for training object detection models.

### YOLO Format Specification

Each annotation line:
```
<class_id> <x_center> <y_center> <width> <height>
```

All values normalized between 0 and 1.

---

## API Endpoints

### 1. Export Image Annotations (YOLO)

**Endpoint**: `GET /export/yolo/image/<file_id>`

**Authentication**: JWT Required

**Response**: `.txt` file with YOLO format annotations

---

### 2. Export Video Annotations (YOLO)

**Endpoint**: `GET /export/yolo/video/<video_id>`

**Authentication**: JWT Required

**Response**: `.zip` file containing:
- `frame_0001.txt`, `frame_0002.txt`, ... (per-frame annotations)
- `classes.txt` (label to class_id mapping)

---

## cURL Examples

### Export Image Annotations

```bash
# Export YOLO annotations for image
curl -X GET http://localhost:5000/export/yolo/image/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o image_annotations.txt

# View the content
cat image_annotations.txt
```

**Example Output** (`image_annotations.txt`):
```
0 0.500000 0.400000 0.200000 0.300000
1 0.750000 0.600000 0.150000 0.250000
0 0.300000 0.500000 0.180000 0.280000
```

### Export Video Annotations

```bash
# Export YOLO annotations for video
curl -X GET http://localhost:5000/export/yolo/video/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o video_annotations_yolo.zip

# Extract and view
unzip video_annotations_yolo.zip
ls -la
# Output:
# frame_0001.txt
# frame_0002.txt
# frame_0003.txt
# ...
# classes.txt

# View a frame's annotations
cat frame_0001.txt
```

**Example Output** (`frame_0001.txt`):
```
0 0.512345 0.423456 0.234567 0.345678
1 0.678901 0.567890 0.123456 0.234567
```

**Example Output** (`classes.txt`):
```
# YOLO Classes Mapping
# Format: class_id label

0 person
1 car
2 dog
```

---

## Axios Examples

### Export Image Annotations

```javascript
// Export YOLO annotations for image
const exportYoloImage = async (fileId, token) => {
  try {
    const response = await axios.get(`/export/yolo/image/${fileId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      responseType: 'blob'
    });
    
    // Trigger download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'annotations.txt');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    console.log('YOLO annotations downloaded successfully');
    
  } catch (error) {
    console.error('Export failed:', error.response?.data?.error);
  }
};

// Usage
exportYoloImage(1, userToken);
```

### Export Video Annotations

```javascript
// Export YOLO annotations for video (with progress indicator)
const exportYoloVideo = async (videoId, token) => {
  try {
    // Show loading indicator
    showLoading('Generating YOLO annotations...');
    
    const response = await axios.get(`/export/yolo/video/${videoId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      responseType: 'blob',
      timeout: 180000, // 3 minute timeout
      onDownloadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          updateProgress(percentCompleted);
        }
      }
    });
    
    hideLoading();
    
    // Trigger download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'video_yolo_annotations.zip');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    console.log('YOLO annotations ZIP downloaded successfully');
    
  } catch (error) {
    hideLoading();
    if (error.code === 'ECONNABORTED') {
      showError('Export timed out. Please try again.');
    } else {
      showError('Export failed: ' + error.response?.data?.error);
    }
  }
};

// Usage
exportYoloVideo(1, userToken);
```

---

## Vue.js Component Example

```vue
<template>
  <div class="yolo-export">
    <h3>Export Annotations</h3>
    
    <div class="export-buttons">
      <button @click="exportImageYolo" :disabled="loading">
        <i class="icon-download"></i>
        Export Image (YOLO)
      </button>
      
      <button @click="exportVideoYolo" :disabled="loading">
        <i class="icon-download"></i>
        Export Video (YOLO)
      </button>
    </div>
    
    <div v-if="loading" class="loading">
      <spinner />
      <p>{{ loadingMessage }}</p>
    </div>
    
    <div v-if="error" class="error">
      {{ error }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['fileId', 'videoId', 'token'],
  data() {
    return {
      loading: false,
      loadingMessage: '',
      error: null
    };
  },
  methods: {
    async exportImageYolo() {
      if (!this.fileId) {
        this.error = 'No image selected';
        return;
      }
      
      this.loading = true;
      this.loadingMessage = 'Generating YOLO annotations...';
      this.error = null;
      
      try {
        const response = await axios.get(
          `/export/yolo/image/${this.fileId}`,
          {
            headers: { 'Authorization': `Bearer ${this.token}` },
            responseType: 'blob'
          }
        );
        
        // Download file
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'annotations.txt');
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        
        this.$emit('export-success', 'YOLO annotations downloaded');
        
      } catch (error) {
        this.error = error.response?.data?.error || 'Export failed';
      } finally {
        this.loading = false;
      }
    },
    
    async exportVideoYolo() {
      if (!this.videoId) {
        this.error = 'No video selected';
        return;
      }
      
      this.loading = true;
      this.loadingMessage = 'Generating YOLO annotations for video...';
      this.error = null;
      
      try {
        const response = await axios.get(
          `/export/yolo/video/${this.videoId}`,
          {
            headers: { 'Authorization': `Bearer ${this.token}` },
            responseType: 'blob',
            timeout: 180000,
            onDownloadProgress: (progressEvent) => {
              if (progressEvent.total) {
                const percent = Math.round(
                  (progressEvent.loaded * 100) / progressEvent.total
                );
                this.loadingMessage = `Downloading... ${percent}%`;
              }
            }
          }
        );
        
        // Download ZIP file
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'video_yolo_annotations.zip');
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        
        this.$emit('export-success', 'YOLO annotations ZIP downloaded');
        
      } catch (error) {
        if (error.code === 'ECONNABORTED') {
          this.error = 'Export timed out. Please try again.';
        } else {
          this.error = error.response?.data?.error || 'Export failed';
        }
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.yolo-export {
  padding: 20px;
}

.export-buttons {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.export-buttons button {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.export-buttons button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 20px;
}

.error {
  color: red;
  padding: 10px;
  background: #fee;
  border-radius: 4px;
}
</style>
```

---

## Complete Workflow Example

```javascript
// Complete workflow: Upload → Annotate → Export YOLO

const completeWorkflow = async () => {
  try {
    // 1. Login
    const loginResponse = await axios.post('/auth/login', {
      email: 'user@example.com',
      password: 'password123'
    });
    const token = loginResponse.data.access_token;
    
    // 2. Upload image
    const formData = new FormData();
    formData.append('file', imageFile);
    
    const uploadResponse = await axios.post('/files/upload', formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    });
    const fileId = uploadResponse.data.file_id;
    
    // 3. Create annotations
    const annotations = [
      { file_id: fileId, label: 'person', x: 100, y: 150, width: 200, height: 300 },
      { file_id: fileId, label: 'car', x: 400, y: 200, width: 150, height: 100 }
    ];
    
    for (const ann of annotations) {
      await axios.post('/annotations/image', ann, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
    }
    
    // 4. Export to YOLO format
    const yoloResponse = await axios.get(`/export/yolo/image/${fileId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
      responseType: 'blob'
    });
    
    // 5. Download YOLO file
    const url = window.URL.createObjectURL(new Blob([yoloResponse.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'annotations.txt');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    console.log('✅ Complete workflow finished successfully');
    
  } catch (error) {
    console.error('❌ Workflow failed:', error.response?.data?.error);
  }
};
```

---

## Error Handling

```javascript
const exportWithErrorHandling = async (fileId, token) => {
  try {
    const response = await axios.get(`/export/yolo/image/${fileId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
      responseType: 'blob'
    });
    
    return { success: true, data: response.data };
    
  } catch (error) {
    if (error.response) {
      const status = error.response.status;
      
      switch (status) {
        case 400:
          return { success: false, error: 'Invalid request or file type' };
        case 401:
          // Token expired
          localStorage.removeItem('token');
          window.location.href = '/login';
          return { success: false, error: 'Session expired' };
        case 404:
          return { success: false, error: 'File not found or access denied' };
        case 500:
          return { success: false, error: 'Server error. Please try again.' };
        default:
          return { success: false, error: error.response.data.error };
      }
    } else if (error.request) {
      return { success: false, error: 'Network error. Check your connection.' };
    } else {
      return { success: false, error: 'Request failed. Please try again.' };
    }
  }
};
```

---

## Testing

```bash
# Test image export
curl -X GET http://localhost:5000/export/yolo/image/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o test_image.txt

# Verify format
cat test_image.txt
# Expected: Lines with format "class_id x_center y_center width height"
# All values should be between 0 and 1

# Test video export
curl -X GET http://localhost:5000/export/yolo/video/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o test_video.zip

# Extract and verify
unzip test_video.zip
ls *.txt
# Expected: frame_0001.txt, frame_0002.txt, ..., classes.txt

# Verify classes mapping
cat classes.txt
# Expected: class_id and label pairs
```

---

## Notes

1. **Class ID Mapping**: Labels are consistently mapped to class IDs using deterministic hashing
2. **Normalized Values**: All coordinates are normalized to 0-1 range
3. **Empty Frames**: Frames without annotations get empty .txt files
4. **ZIP Structure**: Video exports include all frame annotations + classes.txt
5. **Long-Running**: Video exports may take time for long videos - implement timeout handling
