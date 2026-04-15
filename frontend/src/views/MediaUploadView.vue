<!-- src/views/MediaUploadView.vue -->
<template>
  <div class="upload-view">
    <div class="upload-header">
      <div>
        <h2 class="page-title">Upload Media</h2>
        <p class="page-subtitle">Upload images or videos for annotation</p>
      </div>
      <router-link to="/media/library" class="secondary-btn">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M3 4C3 3.46957 3.21071 2.96086 3.58579 2.58579C3.96086 2.21071 4.46957 2 5 2H8L10 5H15C15.5304 5 16.0391 5.21071 16.4142 5.58579C16.7893 5.96086 17 6.46957 17 7V15C17 15.5304 16.7893 16.0391 16.4142 16.4142C16.0391 16.7893 15.5304 17 15 17H5C4.46957 17 3.96086 16.7893 3.58579 16.4142C3.21071 16.0391 3 15.5304 3 15V4Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        View Library
      </router-link>
    </div>

    <!-- Upload Zone -->
    <div 
      class="upload-zone"
      :class="{ 
        'drag-over': isDragging,
        'uploading': mediaStore.uploading
      }"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        multiple
        accept="image/jpeg,image/jpg,image/png,video/mp4,video/avi"
        @change="handleFileSelect"
        style="display: none"
      />

      <div v-if="!mediaStore.uploading" class="upload-content">
        <div class="upload-icon">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <path d="M56 40V50.6667C56 52.0812 55.4381 53.4377 54.4379 54.4379C53.4377 55.4381 52.0812 56 50.6667 56H13.3333C11.9188 56 10.5623 55.4381 9.5621 54.4379C8.5619 53.4377 8 52.0812 8 50.6667V40" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M45.3333 21.3333L32 8L18.6667 21.3333" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M32 8V40" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3 class="upload-title">Drop files here or click to upload</h3>
        <p class="upload-description">
          Supports: JPG, PNG (images) • MP4, AVI (videos)
        </p>
        <p class="upload-limit">Maximum file size: 100MB</p>
      </div>

      <!-- Upload Progress -->
      <div v-else class="upload-progress-container">
        <div class="upload-spinner">
          <div class="spinner"></div>
        </div>
        <p class="upload-status">Uploading {{ currentUploadName }}...</p>
        <div class="progress-bar-container">
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: mediaStore.uploadProgress + '%' }"
            ></div>
          </div>
          <span class="progress-text">{{ mediaStore.uploadProgress }}%</span>
        </div>
      </div>
    </div>

    <!-- File Type Guide -->
    <div class="upload-guide">
      <div class="guide-card">
        <div class="guide-icon image">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
            <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
            <path d="M21 15L16 10L5 21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="guide-content">
          <h4>Images</h4>
          <p>JPG, PNG • Max 50MB</p>
        </div>
      </div>

      <div class="guide-card">
        <div class="guide-icon video">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M23 7L16 12L23 17V7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <rect x="1" y="5" width="15" height="14" rx="2" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <div class="guide-content">
          <h4>Videos</h4>
          <p>MP4, AVI • Max 100MB</p>
        </div>
      </div>
    </div>

    <!-- Recent Uploads -->
    <div v-if="recentUploads.length > 0" class="recent-uploads">
      <h3 class="section-title">Recent Uploads</h3>
      <div class="uploads-grid">
        <div 
          v-for="upload in recentUploads" 
          :key="upload.id"
          class="upload-item"
          :class="{ 'upload-item-clickable': typeof upload.id === 'number' }"
          @click="navigateToAnnotation(upload)"
          :title="typeof upload.id === 'number' ? `Click to annotate ${upload.name}` : ''"
        >
          <div class="upload-thumbnail">
            <img 
              v-if="upload.mediaType === 'image'" 
              :src="getMediaUrl(upload.url)" 
              :alt="upload.name"
              @error="handleImageError"
            />
            <div v-else class="video-placeholder">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <path d="M30 10L20 16L30 22V10Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <rect x="2" y="6" width="18" height="20" rx="2" stroke="white" stroke-width="2"/>
              </svg>
            </div>
          </div>
          <div class="upload-info">
            <div class="upload-name">{{ upload.name }}</div>
            <div class="upload-meta">
              <span class="upload-type">{{ upload.mediaType }}</span>
              <span class="upload-date">{{ formatDate(upload.uploadedAt) }}</span>
            </div>
          </div>
          <div class="upload-status success">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M13.3333 4L6 11.3333L2.66667 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Toast -->
    <transition name="toast">
      <div v-if="showError" class="toast error">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2"/>
          <path d="M10 6V10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <circle cx="10" cy="14" r="0.5" fill="currentColor"/>
        </svg>
        <span>{{ errorMessage }}</span>
        <button @click="closeError" class="toast-close">×</button>
      </div>
    </transition>

    <!-- Success Toast -->
    <transition name="toast">
      <div v-if="showSuccess" class="toast success">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2"/>
          <path d="M6 10L9 13L14 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>{{ successMessage }}</span>
        <button @click="closeSuccess" class="toast-close">×</button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMediaStore } from '../stores/mediaStore'
import { getFileUrl } from '../config/api'

const router = useRouter()

const mediaStore = useMediaStore()

const fileInput = ref(null)
const isDragging = ref(false)
const currentUploadName = ref('')
const recentUploads = ref([])
const showError = ref(false)
const showSuccess = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png']
const ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/avi']
const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100MB

function validateFile(file) {
  const isImage = ALLOWED_IMAGE_TYPES.includes(file.type)
  const isVideo = ALLOWED_VIDEO_TYPES.includes(file.type)

  if (!isImage && !isVideo) {
    return {
      valid: false,
      error: `Invalid file type: ${file.name}. Only JPG, PNG, MP4, AVI allowed.`
    }
  }

  if (file.size > MAX_FILE_SIZE) {
    return {
      valid: false,
      error: `File too large: ${file.name}. Maximum size is 100MB.`
    }
  }

  return { valid: true }
}

async function uploadFile(file) {
  currentUploadName.value = file.name

  try {
    const response = await mediaStore.uploadMedia(file)
    
    recentUploads.value.unshift({
      id: response.id || Date.now(),
      name: file.name,
      mediaType: file.type.startsWith('video/') ? 'video' : 'image',
      url: response.file_path || response.url,
      uploadedAt: new Date().toISOString()
    })

    showSuccessToast(`Successfully uploaded ${file.name}`)
  } catch (err) {
    showErrorToast(mediaStore.error || `Failed to upload ${file.name}`)
  }
}

function navigateToAnnotation(upload) {
  if (!upload.id || typeof upload.id !== 'number') return
  if (upload.mediaType === 'video') {
    router.push(`/videos/${upload.id}`)
  } else {
    router.push(`/annotate/${upload.id}`)
  }
}

async function handleFiles(files) {
  const fileArray = Array.from(files)

  for (const file of fileArray) {
    const validation = validateFile(file)
    
    if (!validation.valid) {
      showErrorToast(validation.error)
      continue
    }

    await uploadFile(file)
  }
}

function handleFileSelect(event) {
  const files = event.target.files
  if (files && files.length > 0) {
    handleFiles(files)
  }
  // Reset input
  event.target.value = ''
}

function handleDragOver(event) {
  isDragging.value = true
}

function handleDragLeave(event) {
  isDragging.value = false
}

function handleDrop(event) {
  isDragging.value = false
  const files = event.dataTransfer.files
  if (files && files.length > 0) {
    handleFiles(files)
  }
}

function triggerFileInput() {
  if (!mediaStore.uploading) {
    fileInput.value?.click()
  }
}

function getMediaUrl(filePath) {
  if (!filePath) return ''
  if (filePath.startsWith('http')) return filePath
  
  // Extract just the filename from the path
  const filename = filePath.split('\\').pop().split('/').pop()
  
  // Use the getFileUrl helper
  const url = getFileUrl(filename)
  console.log('[MediaUploadView] getMediaUrl:', { filePath, filename, url })
  return url
}

function formatDate(dateString) {
  if (!dateString) return 'Just now'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
  return date.toLocaleDateString()
}

function showErrorToast(message) {
  errorMessage.value = message
  showError.value = true
  setTimeout(() => {
    showError.value = false
  }, 5000)
}

function showSuccessToast(message) {
  successMessage.value = message
  showSuccess.value = true
  setTimeout(() => {
    showSuccess.value = false
  }, 3000)
}

function closeError() {
  showError.value = false
}

function closeSuccess() {
  showSuccess.value = false
}

function handleImageError(event) {
  console.error('[MediaUploadView] Image failed to load:', event.target.src)
  event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="64" height="64"%3E%3Crect fill="%23f3f4f6" width="64" height="64"/%3E%3Ctext fill="%239ca3af" font-family="sans-serif" font-size="10" dy="35" dx="8"%3ENo image%3C/text%3E%3C/svg%3E'
}

</script>

<style scoped>
.upload-view {
  max-width: 1200px;
  margin: 0 auto;
}

.upload-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 15px;
  color: #6b7280;
  margin: 0;
}

.secondary-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: white;
  color: #4F46E5;
  border: 2px solid #4F46E5;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.secondary-btn:hover {
  background: #4F46E5;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

.upload-zone {
  background: white;
  border: 3px dashed #d1d5db;
  border-radius: 16px;
  padding: 64px 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 32px;
}

.upload-zone:hover {
  border-color: #4F46E5;
  background: #fafafa;
}

.upload-zone.drag-over {
  border-color: #4F46E5;
  background: #eef2ff;
  transform: scale(1.02);
}

.upload-zone.uploading {
  cursor: not-allowed;
  border-color: #9ca3af;
  background: #f9fafb;
}

.upload-content {
  pointer-events: none;
}

.upload-icon {
  margin: 0 auto 24px;
  color: #9ca3af;
  transition: all 0.3s ease;
}

.upload-zone:hover .upload-icon {
  color: #4F46E5;
  transform: translateY(-4px);
}

.upload-title {
  font-size: 20px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 8px 0;
}

.upload-description {
  font-size: 15px;
  color: #6b7280;
  margin: 0 0 4px 0;
}

.upload-limit {
  font-size: 13px;
  color: #9ca3af;
  margin: 0;
}

.upload-progress-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.upload-spinner {
  width: 64px;
  height: 64px;
}

.spinner {
  width: 100%;
  height: 100%;
  border: 6px solid #e5e7eb;
  border-top: 6px solid #4F46E5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.upload-status {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.progress-bar-container {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
  max-width: 400px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: #4F46E5;
  min-width: 48px;
}

.upload-guide {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 48px;
}

.guide-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
}

.guide-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.guide-icon.image {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.guide-icon.video {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.guide-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 4px 0;
}

.guide-content p {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
}

.recent-uploads {
  margin-top: 48px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 20px 0;
}

.uploads-grid {
  display: grid;
  gap: 16px;
}

.upload-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.upload-item:hover {
  border-color: #d1d5db;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.upload-item-clickable {
  cursor: pointer;
}

.upload-item-clickable:hover {
  border-color: #1a1a1a;
  box-shadow: 3px 3px 0px #1a1a1a;
  transform: translate(-1px, -1px);
}

.upload-thumbnail {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f3f4f6;
}

.upload-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.upload-info {
  flex: 1;
  min-width: 0;
}

.upload-name {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upload-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #6b7280;
}

.upload-type {
  padding: 2px 8px;
  background: #f3f4f6;
  border-radius: 4px;
  text-transform: capitalize;
  font-weight: 500;
}

.upload-status {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.upload-status.success {
  background: #d1fae5;
  color: #059669;
}

.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-width: 400px;
}

.toast.error {
  border-left: 4px solid #ef4444;
  color: #991b1b;
}

.toast.success {
  border-left: 4px solid #10b981;
  color: #065f46;
}

.toast-close {
  background: none;
  border: none;
  font-size: 24px;
  color: currentColor;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.toast-close:hover {
  opacity: 1;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

@media (max-width: 768px) {
  .upload-header {
    flex-direction: column;
    gap: 16px;
  }

  .upload-zone {
    padding: 48px 24px;
  }

  .upload-guide {
    grid-template-columns: 1fr;
  }

  .toast {
    bottom: 16px;
    right: 16px;
    left: 16px;
    max-width: none;
  }
}
</style>