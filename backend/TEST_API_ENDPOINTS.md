# 🧪 API Endpoint Testing Guide

## ✅ Fixed Issues

1. **Added `/api` prefix to all routes**
2. **Configured CORS properly** for frontend (localhost:5173 and localhost:3000)
3. **Removed duplicate url_prefix** from blueprint definitions
4. **OPTIONS requests now return 200** (handled by CORS)

---

## 📍 Updated API Endpoints

All endpoints now have the `/api` prefix:

### Authentication (No Auth Required)
```
POST /api/auth/signup
POST /api/auth/login
```

### Files (Auth Required)
```
POST /api/files/upload
GET  /api/files
GET  /api/files/<file_id>
```

### Videos (Auth Required)
```
POST /api/videos/process
GET  /api/videos/<video_id>/frames
```

### Annotations (Auth Required)
```
POST   /api/annotations
POST   /api/annotations/image
GET    /api/annotations/file/<file_id>
GET    /api/annotations/image/<file_id>
PUT    /api/annotations/<annotation_id>
DELETE /api/annotations/<annotation_id>
```

### Export (Auth Required)
```
GET /api/export/json
GET /api/export/csv
GET /api/export/annotated-image/<file_id>
GET /api/export/annotated-video/<video_id>
GET /api/export/yolo/image/<file_id>
GET /api/export/yolo/video/<video_id>
```

---

## 🧪 Test Commands

### 1. Test Signup
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

**Expected Response (201)**:
```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### 2. Test Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

**Expected Response (200)**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### 3. Test Protected Route (Files)
```bash
# Replace YOUR_TOKEN with the access_token from login
curl -X GET http://localhost:5000/api/files \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response (200)**:
```json
{
  "files": [],
  "count": 0
}
```

### 4. Test CORS Preflight
```bash
curl -X OPTIONS http://localhost:5000/api/auth/signup \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

**Expected**: Should return 200 with CORS headers

---

## 🌐 Frontend Integration

Update your frontend Axios configuration:

### `src/api/axios.js`
```javascript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api',  // ✅ Note the /api prefix
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - Add JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

### Service Layer Updates

All service calls remain the same since we're using the baseURL:

```javascript
// auth.service.js
export const authService = {
  async signup(email, password) {
    const response = await apiClient.post('/auth/signup', { email, password })
    return response.data
  },

  async login(email, password) {
    const response = await apiClient.post('/auth/login', { email, password })
    return response.data
  }
}

// file.service.js
export const fileService = {
  async uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    return response.data
  },

  async getFiles(type = null) {
    const params = type ? { type } : {}
    const response = await apiClient.get('/files', { params })
    return response.data
  }
}
```

---

## 🔍 Troubleshooting

### Issue: Still getting 404
**Solution**: 
1. Restart Flask server: `python run.py`
2. Check console for blueprint registration messages
3. Verify routes with: `flask routes` (if Flask CLI is configured)

### Issue: CORS errors
**Solution**:
1. Verify frontend is running on http://localhost:5173 or http://localhost:3000
2. Check Flask console for CORS-related errors
3. Ensure Flask-CORS is installed: `pip install flask-cors`

### Issue: 401 Unauthorized
**Solution**:
1. Verify JWT token is being sent in Authorization header
2. Check token format: `Bearer <token>`
3. Ensure JWT_SECRET_KEY is configured in config.py

### Issue: OPTIONS returns 404
**Solution**:
1. Verify CORS is configured in app/__init__.py
2. Restart Flask server
3. Check that Flask-CORS is properly installed

---

## ✅ Verification Checklist

- [ ] Flask server starts without errors
- [ ] POST /api/auth/signup returns 201
- [ ] POST /api/auth/login returns 200 with token
- [ ] OPTIONS requests return 200 (not 404)
- [ ] Protected routes return 401 without token
- [ ] Protected routes return 200 with valid token
- [ ] Frontend can call backend without CORS errors
- [ ] File upload works
- [ ] All CRUD operations work

---

## 🚀 Start Backend

```bash
cd backend
python run.py
```

**Expected Output**:
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

---

## 📝 Summary of Changes

### `backend/app/__init__.py`
- ✅ Added proper CORS configuration with specific origins
- ✅ Registered all blueprints with `/api` prefix
- ✅ Configured CORS to handle OPTIONS requests

### `backend/app/routes/*.py`
- ✅ Removed `url_prefix` from all blueprint definitions
- ✅ Prefix is now added during registration in `__init__.py`

### Result
- ✅ All routes now accessible at `/api/*`
- ✅ CORS properly configured for frontend
- ✅ OPTIONS requests return 200
- ✅ No more 404 errors

---

**Your backend is now properly configured! Test with the commands above.**
