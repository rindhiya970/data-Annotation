<!-- src/views/VideoDetailView.vue -->
<template>
  <div class="video-detail-view">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <button @click="goBack" class="back-btn">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Back
        </button>
        <div>
          <h1 class="title">{{ file?.original_filename || 'Loading...' }}</h1>
          <p class="subtitle">Video Player</p>
        </div>
      </div>
      <div class="header-actions">
        <button @click="downloadVideo" class="secondary-btn">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M14 10V12.6667C14 13.0203 13.8595 13.3594 13.6095 13.6095C13.3594 13.8595 13.0203 14 12.6667 14H3.33333C2.97971 14 2.64057 13.8595 2.39052 13.6095C2.14048 13.3594 2 13.0203 2 12.6667V10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4.66667 6.66667L8 10L11.3333 6.66667" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8 10V2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Download
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading video...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
        <circle cx="24" cy="24" r="20" stroke="#ef4444" stroke-width="2"/>
        <path d="M24 14V26" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/>
        <circle cx="24" cy="32" r="1.5" fill="#ef4444"/>
      </svg>
      <h3>{{ error }}</h3>
      <button @click="loadFile" class="retry-btn">Try Again</button>
    </div>

    <!-- Video Player -->
    <div v-else class="content">
      <div class="video-container">
        <video 
          ref="videoPlayer"
          :src="videoUrl"
          controls
          controlsList="nodownload"
          class="video-player"
          @loadedmetadata="handleVideoLoaded"
          @error="handleVideoError"
        >
          Your browser does not support the video tag.
        </video>
      </div>

      <!-- Video Info -->
      <div class="video-info-panel">
        <h3>Video Information</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">Filename:</span>
            <span class="info-value">{{ file?.original_filename }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">File Type:</span>
            <span class="info-value">{{ file?.file_type }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Uploaded:</span>
            <span class="info-value">{{ formatDate(file?.created_at) }}</span>
          </div>
          <div class="info-item" v-if="videoMetadata.duration">
            <span class="info-label">Duration:</span>
            <span class="info-value">{{ formatDuration(videoMetadata.duration) }}</span>
          </div>
          <div class="info-item" v-if="videoMetadata.width">
            <span class="info-label">Resolution:</span>
            <span class="info-value">{{ videoMetadata.width }} × {{ videoMetadata.height }}</span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="action-buttons">
          <button @click="processVideo" class="action-btn primary" :disabled="processing">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 2V8L12 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
            </svg>
            {{ processing ? 'Processing...' : 'Process for Annotation' }}
          </button>
          <button @click="deleteVideo" class="action-btn danger">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M2 4H14M5.5 4V2.5C5.5 2.22386 5.72386 2 6 2H10C10.2761 2 10.5 2.22386 10.5 2.5V4M7 7V11M9 7V11M3 4L3.5 12.5C3.5 13.3284 4.17157 14 5 14H11C11.8284 14 12.5 13.3284 12.5 12.5L13 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            Delete Video
          </button>
        </div>

        <!-- Processing Info -->
        <div v-if="processing" class="processing-info">
          <div class="spinner-small"></div>
          <p>Processing video to extract frames for annotation...</p>
          <p class="processing-note">This may take a few minutes depending on video length.</p>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <transition name="toast">
      <div v-if="showSuccess" class="toast success">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2"/>
          <path d="M6 10L9 13L14 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <span>{{ successMessage }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fileService } from '../services/fileService'
import { getFileUrl } from '../config/api'

const route = useRoute()
const router = useRouter()
const fileId = computed(() => parseInt(route.params.id))

// State
const file = ref(null)
const loading = ref(true)
const error = ref(null)
const processing = ref(false)
const showSuccess = ref(false)
const successMessage = ref('')

// Video refs
const videoPlayer = ref(null)
const videoMetadata = ref({
  duration: 0,
  width: 0,
  height: 0
})

const videoUrl = computed(() => {
  if (!file.value) return ''
  return getFileUrl(file.value.stored_filename)
})

async function loadFile() {
  loading.value = true
  error.value = null
  
  try {
    const response = await fileService.getFile(fileId.value)
    if (response.success && response.data && response.data.file) {
      file.value = response.data.file
      
      if (file.value.file_type !== 'video') {
        error.value = 'This file is not a video'
      }
    } else {
      error.value = 'Video not found'
    }
  } catch (err) {
    console.error('Failed to load video:', err)
    error.value = 'Failed to load video'
  } finally {
    loading.value = false
  }
}

function handleVideoLoaded(event) {
  const video = event.target
  videoMetadata.value = {
    duration: video.duration,
    width: video.videoWidth,
    height: video.videoHeight
  }
  console.log('[VideoDetail] Video loaded:', videoMetadata.value)
}

function handleVideoError(event) {
  console.error('[VideoDetail] Video error:', event)
  error.value = 'Failed to load video file. The file may be corrupted or in an unsupported format.'
}

function formatDate(dateString) {
  if (!dateString) return 'Unknown'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDuration(seconds) {
  if (!seconds) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function downloadVideo() {
  if (!file.value) return
  
  const link = document.createElement('a')
  link.href = videoUrl.value
  link.download = file.value.original_filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

async function processVideo() {
  if (!file.value) return
  processing.value = true
  try {
    const token = localStorage.getItem('token')
    // Check if already processed
    const checkRes = await fetch(`http://127.0.0.1:5000/api/videos/by-file/${fileId.value}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (checkRes.ok) {
      const checkData = await checkRes.json()
      if (checkData.success) {
        // Already processed - go straight to annotation
        router.push(`/video-annotate/${fileId.value}`)
        return
      }
    }
    // Process the video
    const res = await fetch('http://127.0.0.1:5000/api/videos/process', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_id: fileId.value })
    })
    const data = await res.json()
    if (data.success) {
      showSuccessToast(`Video processed! ${data.data.total_frames} frames extracted.`)
      setTimeout(() => router.push(`/video-annotate/${fileId.value}`), 1000)
    } else {
      alert(data.message || 'Processing failed')
    }
  } catch (err) {
    console.error('Failed to process video:', err)
    alert('Failed to process video')
  } finally {
    processing.value = false
  }
}

async function deleteVideo() {
  if (!file.value) return
  
  if (!confirm(`Are you sure you want to delete "${file.value.original_filename}"?`)) {
    return
  }
  
  try {
    await fileService.deleteFile(fileId.value)
    showSuccessToast('Video deleted successfully')
    setTimeout(() => {
      router.push('/media/library')
    }, 1000)
  } catch (err) {
    console.error('Failed to delete video:', err)
    alert('Failed to delete video')
  }
}

function showSuccessToast(message) {
  successMessage.value = message
  showSuccess.value = true
  setTimeout(() => {
    showSuccess.value = false
  }, 3000)
}

function goBack() {
  router.push('/media/library')
}

onMounted(() => {
  loadFile()
})
</script>

<style scoped>
.video-detail-view {
  max-width: 1600px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  border-color: #4F46E5;
  color: #4F46E5;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.secondary-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: white;
  color: #4F46E5;
  border: 2px solid #4F46E5;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.secondary-btn:hover {
  background: #4F46E5;
  color: white;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #4F46E5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-small {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #4F46E5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-container h3 {
  margin: 16px 0;
  color: #ef4444;
}

.retry-btn {
  padding: 10px 20px;
  background: #4F46E5;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
}

.video-container {
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 16/9;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-player {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.video-info-panel {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  height: fit-content;
}

.video-info-panel h3 {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 20px 0;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 14px;
  color: #111827;
  word-break: break-word;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.primary {
  background: #4F46E5;
  color: white;
}

.action-btn.primary:hover:not(:disabled) {
  background: #4338CA;
}

.action-btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.danger {
  background: white;
  color: #ef4444;
  border: 2px solid #ef4444;
}

.action-btn.danger:hover {
  background: #ef4444;
  color: white;
}

.processing-info {
  margin-top: 20px;
  padding: 16px;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}

.processing-info p {
  margin: 0;
  font-size: 14px;
  color: #0369a1;
}

.processing-note {
  font-size: 12px !important;
  color: #0284c7 !important;
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
  border-radius: 8px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  z-index: 1000;
}

.toast.success {
  border-left: 4px solid #10b981;
  color: #065f46;
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

@media (max-width: 1024px) {
  .content {
    grid-template-columns: 1fr;
  }
  
  .video-container {
    aspect-ratio: 16/9;
  }
}
</style>
