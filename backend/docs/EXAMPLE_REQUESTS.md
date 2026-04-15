# Example API Requests

## Complete Workflow Examples

### 1. Image Annotation Workflow

```bash
# Step 1: Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Response: {"access_token":"eyJ0eXAi...","user":{...}}
# Save the access_token

# Step 2: Upload Image
curl -X POST http://localhost:5000/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/image.jpg"

# Response: {"file_id":1,"original_filename":"image.jpg","message":"File uploaded successfully"}

# Step 3: Create Annotation on Image
curl -X POST http://localhost:5000/annotations/image \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": 1,
    "label": "person",
    "x": 100.0,
    "y": 150.0,
    "width": 200.0,
    "height": 300.0
  }'

# Step 4: Get All Annotations for Image
curl -X GET http://localhost:5000/annotations/image/1 \
  -H "Authorization: Bearer YOUR_TOKEN"

# Step 5: Export Annotated Image
curl -X GET http://localhost:5000/export/annotated-image/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o annotated_image.jpg
```

### 2. Video Annotation Workflow

```bash
# Step 1: Login (same as above)

# Step 2: Upload Video
curl -X POST http://localhost:5000/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/video.mp4"

# Response: {"file_id":2,"original_filename":"video.mp4","message":"File uploaded successfully"}

# Step 3: Process Video (Extract Frames)
curl -X POST http://localhost:5000/videos/process \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"file_id": 2}'

# Response: {"video_id":1,"total_frames":120,"fps":30.0,"duration":4.0,"message":"Video processed successfully"}

# Step 4: Get Frames
curl -X GET http://localhost:5000/videos/1/frames \
  -H "Authorization: Bearer YOUR_TOKEN"

# Step 5: Create Annotation on Frame
curl -X POST http://localhost:5000/annotations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "frame_id": 5,
    "label": "car",
    "x": 150.0,
    "y": 200.0,
    "width": 100.0,
    "height": 80.0
  }'

# Step 6: Export Annotated Video
curl -X GET http://localhost:5000/export/annotated-video/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o annotated_video.mp4
```

---

## JavaScript/Axios Examples

### Image Annotation

```javascript
// 1. Login
const loginResponse = await axios.post('/auth/login', {
  email: 'user@example.com',
  password: 'password123'
});
const token = loginResponse.data.access_token;

// 2. Upload Image
const formData = new FormData();
formData.append('file', imageFile);

const uploadResponse = await axios.post('/files/upload', formData, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'multipart/form-data'
  }
});
const fileId = uploadResponse.data.file_id;

// 3. Create Annotation
const annotationResponse = await axios.post('/annotations/image', {
  file_id: fileId,
  label: 'person',
  x: 100.0,
  y: 150.0,
  width: 200.0,
  height: 300.0
}, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// 4. Get Annotations
const getResponse = await axios.get(`/annotations/image/${fileId}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const annotations = getResponse.data.annotations;

// 5. Download Annotated Image
const exportResponse = await axios.get(`/export/annotated-image/${fileId}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  },
  responseType: 'blob'
});

// Trigger download
const url = window.URL.createObjectURL(new Blob([exportResponse.data]));
const link = document.createElement('a');
link.href = url;
link.setAttribute('download', 'annotated_image.jpg');
document.body.appendChild(link);
link.click();
link.remove();
window.URL.revokeObjectURL(url);
```

### Video Annotation with Progress

```javascript
// Process video with loading indicator
const processVideo = async (fileId) => {
  try {
    showLoading('Processing video... This may take a few minutes');
    
    const response = await axios.post('/videos/process', 
      { file_id: fileId },
      {
        headers: { 'Authorization': `Bearer ${token}` },
        timeout: 180000 // 3 minute timeout
      }
    );
    
    hideLoading();
    return response.data;
  } catch (error) {
    hideLoading();
    if (error.code === 'ECONNABORTED') {
      showError('Video processing timed out. Please try a shorter video.');
    } else {
      showError('Video processing failed: ' + error.response?.data?.error);
    }
  }
};

// Export annotated video with progress
const exportAnnotatedVideo = async (videoId) => {
  try {
    showLoading('Generating annotated video...');
    
    const response = await axios.get(`/export/annotated-video/${videoId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
      responseType: 'blob',
      timeout: 300000, // 5 minute timeout
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
    link.setAttribute('download', 'annotated_video.mp4');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
  } catch (error) {
    hideLoading();
    showError('Export failed: ' + error.response?.data?.error);
  }
};
```

---

## Vue.js Component Examples

### Image Annotation Component

```vue
<template>
  <div class="image-annotation">
    <div class="canvas-container">
      <canvas ref="canvas" @mousedown="startDrawing" @mousemove="draw" @mouseup="endDrawing"></canvas>
    </div>
    
    <div class="controls">
      <input v-model="currentLabel" placeholder="Label" />
      <button @click="saveAnnotation" :disabled="!currentBox">Save Annotation</button>
      <button @click="exportAnnotatedImage">Export Annotated Image</button>
    </div>
    
    <div class="annotations-list">
      <h3>Annotations</h3>
      <div v-for="ann in annotations" :key="ann.id" class="annotation-item">
        {{ ann.label }} - ({{ ann.x }}, {{ ann.y }}, {{ ann.width }}, {{ ann.height }})
        <button @click="deleteAnnotation(ann.id)">Delete</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['fileId', 'token'],
  data() {
    return {
      annotations: [],
      currentLabel: '',
      currentBox: null,
      isDrawing: false,
      startX: 0,
      startY: 0
    };
  },
  mounted() {
    this.loadImage();
    this.loadAnnotations();
  },
  methods: {
    async loadImage() {
      // Load and display image on canvas
      const response = await axios.get(`/files/${this.fileId}`, {
        headers: { 'Authorization': `Bearer ${this.token}` }
      });
      // Draw image on canvas...
    },
    
    async loadAnnotations() {
      const response = await axios.get(`/annotations/image/${this.fileId}`, {
        headers: { 'Authorization': `Bearer ${this.token}` }
      });
      this.annotations = response.data.annotations;
    },
    
    startDrawing(e) {
      this.isDrawing = true;
      const rect = this.$refs.canvas.getBoundingClientRect();
      this.startX = e.clientX - rect.left;
      this.startY = e.clientY - rect.top;
    },
    
    draw(e) {
      if (!this.isDrawing) return;
      const rect = this.$refs.canvas.getBoundingClientRect();
      const currentX = e.clientX - rect.left;
      const currentY = e.clientY - rect.top;
      
      this.currentBox = {
        x: Math.min(this.startX, currentX),
        y: Math.min(this.startY, currentY),
        width: Math.abs(currentX - this.startX),
        height: Math.abs(currentY - this.startY)
      };
      
      // Redraw canvas with current box...
    },
    
    endDrawing() {
      this.isDrawing = false;
    },
    
    async saveAnnotation() {
      if (!this.currentBox || !this.currentLabel) {
        alert('Please draw a box and enter a label');
        return;
      }
      
      try {
        const response = await axios.post('/annotations/image', {
          file_id: this.fileId,
          label: this.currentLabel,
          x: this.currentBox.x,
          y: this.currentBox.y,
          width: this.currentBox.width,
          height: this.currentBox.height
        }, {
          headers: { 'Authorization': `Bearer ${this.token}` }
        });
        
        this.annotations.push(response.data.annotation);
        this.currentBox = null;
        this.currentLabel = '';
        
      } catch (error) {
        alert('Error: ' + error.response?.data?.error);
      }
    },
    
    async exportAnnotatedImage() {
      try {
        const response = await axios.get(`/export/annotated-image/${this.fileId}`, {
          headers: { 'Authorization': `Bearer ${this.token}` },
          responseType: 'blob'
        });
        
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'annotated_image.jpg');
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        
      } catch (error) {
        alert('Export failed: ' + error.response?.data?.error);
      }
    }
  }
};
</script>
```

---

## Error Handling Examples

```javascript
// Comprehensive error handling
const createImageAnnotation = async (data) => {
  try {
    const response = await axios.post('/annotations/image', data, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return { success: true, data: response.data };
    
  } catch (error) {
    if (error.response) {
      // Server responded with error
      const status = error.response.status;
      const message = error.response.data.error;
      
      switch (status) {
        case 400:
          return { success: false, error: `Validation error: ${message}` };
        case 401:
          // Token expired - redirect to login
          localStorage.removeItem('token');
          window.location.href = '/login';
          return { success: false, error: 'Session expired' };
        case 404:
          return { success: false, error: 'File not found' };
        case 500:
          return { success: false, error: 'Server error. Please try again.' };
        default:
          return { success: false, error: message };
      }
    } else if (error.request) {
      // Request made but no response
      return { success: false, error: 'Network error. Please check your connection.' };
    } else {
      // Error in request setup
      return { success: false, error: 'Request failed. Please try again.' };
    }
  }
};
```
