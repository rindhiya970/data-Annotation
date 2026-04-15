// API Configuration for Vue + Flask
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api';

export const API_CONFIG = {
  baseURL: API_BASE_URL,
  endpoints: {
    auth: {
      login: '/auth/login',
      signup: '/auth/signup',
      logout: '/auth/logout',
      me: '/auth/me',
    },
    files: {
      upload: '/files/upload',
      list: '/files',
      getById: (id) => `/files/${id}`,
    },
    videos: {
      list: '/videos',
      process: '/videos/process',
      frames: (id) => `/videos/${id}/frames`,
    },
    annotations: {
      create: '/annotations',
      byFile: (id) => `/annotations/file/${id}`,
      byVideo: (id) => `/annotations/video/${id}`,
      update: (id) => `/annotations/${id}`,
      delete: (id) => `/annotations/${id}`,
    },
    export: {
      json: '/export/json',
      csv: '/export/csv',
      annotatedImage: (id) => `/export/annotated-image/${id}`,
      annotatedVideo: (id) => `/export/annotated-video/${id}`,
      yoloImage: (id) => `/export/yolo/image/${id}`,
      yoloVideo: (id) => `/export/yolo/video/${id}`,
    },
  },
};

/**
 * ⚠️ CRITICAL: Get file URL for displaying images/videos
 * 
 * DO NOT use file_path directly from backend!
 * Backend returns: "uploads\\abc123_file.jpg" (Windows path)
 * 
 * This function converts it to a proper URL:
 * "http://127.0.0.1:5000/uploads/abc123_file.jpg"
 * 
 * @param {string} storedFilename - The stored_filename from backend (e.g., "abc123_image.jpg")
 * @returns {string} Full URL to access the file
 * 
 * Usage in Vue component:
 * <img :src="getFileUrl(file.stored_filename)" />
 */
export const getFileUrl = (storedFilename) => {
  if (!storedFilename) return '';
  
  // Remove /api from base URL for static files
  const baseUrl = API_BASE_URL.replace('/api', '');
  
  // Construct URL using stored_filename directly
  return `${baseUrl}/uploads/${storedFilename}`;
};

/**
 * Alternative: Get file URL from file_path (handles Windows backslashes)
 * 
 * @param {string} filePath - Backend file path (e.g., "uploads\\file.png")
 * @returns {string} Full URL to access the file
 */
export const getFileUrlFromPath = (filePath) => {
  if (!filePath) return '';
  
  // Convert Windows backslashes to forward slashes
  const normalizedPath = filePath.replace(/\\/g, '/');
  
  // Remove leading slash if present
  const cleanPath = normalizedPath.startsWith('/') 
    ? normalizedPath.slice(1) 
    : normalizedPath;
  
  // Remove /api from base URL for static files
  const baseUrl = API_BASE_URL.replace('/api', '');
  
  return `${baseUrl}/${cleanPath}`;
};

/**
 * Get frame URL for video frames
 * 
 * @param {string} framePath - Frame path from backend
 * @returns {string} Full URL to access the frame
 */
export const getFrameUrl = (framePath) => {
  return getFileUrlFromPath(framePath);
};

export default API_CONFIG;

