<!-- src/views/MediaLibraryView.vue -->
<template>
  <div class="library-view">
    <div class="library-header">
      <div>
        <h2 class="page-title">Media Library</h2>
        <p class="page-subtitle">{{ totalCount }} files uploaded</p>
      </div>
      <router-link to="/media/upload" class="primary-btn">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M10 4V16M4 10H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Upload Media
      </router-link>
    </div>

    <!-- Filter Tabs -->
    <div class="filter-tabs">
      <button 
        :class="['tab', { active: activeFilter === 'all' }]"
        @click="activeFilter = 'all'"
      >
        All Media
        <span class="tab-count">{{ totalCount }}</span>
      </button>
      <button 
        :class="['tab', { active: activeFilter === 'image' }]"
        @click="activeFilter = 'image'"
      >
        Images
        <span class="tab-count">{{ imageCount }}</span>
      </button>
      <button 
        :class="['tab', { active: activeFilter === 'video' }]"
        @click="activeFilter = 'video'"
      >
        Videos
        <span class="tab-count">{{ videoCount }}</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="mediaStore.loading" class="loading-container">
      <div class="media-grid skeleton">
        <div v-for="i in 8" :key="i" class="skeleton-card">
          <div class="skeleton-image"></div>
          <div class="skeleton-text"></div>
          <div class="skeleton-text short"></div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredMedia.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
          <path d="M100 100H20V20L40 40L60 20L80 40L100 20V100Z" stroke="#d1d5db" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="40" cy="55" r="8" stroke="#d1d5db" stroke-width="4"/>
          <path d="M100 70L80 50L50 80L20 50" stroke="#d1d5db" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h3>No media files yet</h3>
      <p>Upload your first image or video to get started</p>
      <router-link to="/media/upload" class="empty-btn">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M10 4V16M4 10H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Upload Media
      </router-link>
    </div>

    <!-- Media Grid -->
    <div v-else class="media-grid">
      <div 
        v-for="media in filteredMedia" 
        :key="media.id"
        class="media-card"
      >
        <div class="media-preview">
          <img 
            v-if="media.mediaType === 'image'" 
            :src="getMediaUrl(media.thumbnail || media.url)" 
            :alt="media.name"
            @error="handleImageError"
          />
          <div v-else class="video-preview">
            <div class="video-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <circle cx="24" cy="24" r="20" fill="rgba(255,255,255,0.2)"/>
                <path d="M20 16L32 24L20 32V16Z" fill="white"/>
              </svg>
            </div>
          </div>
          <div class="media-type-badge" :class="media.mediaType">
            <svg v-if="media.mediaType === 'image'" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="2" y="2" width="12" height="12" rx="1" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="6" cy="6" r="1" fill="currentColor"/>
              <path d="M14 10L11 7L4 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M15 5L10 8L15 11V5Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <rect x="1" y="3" width="9" height="10" rx="1" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </div>
        </div>
        <div class="media-info">
          <h3 class="media-name">{{ media.name }}</h3>
          <div class="media-meta">
            <span class="meta-date">{{ formatDate(media.uploadedAt) }}</span>
          </div>
        </div>
        <!-- Always-visible action bar -->
        <div class="media-actions" @click.stop>
          <button class="action-annotate-btn" @click.stop="navigateToAnnotation(media)">
            {{ media.mediaType === 'image' ? ' Annotate' : 'Annotate' }}
          </button>
          <button class="action-delete-btn" @click.stop="deleteMedia(media)">
            🗑 Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Pagination Placeholder -->
    <div v-if="filteredMedia.length > 0" class="pagination">
      <button class="pagination-btn" disabled>
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <span class="pagination-info"></span>
      <button class="pagination-btn" disabled>
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M6 4L10 8L6 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
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
import { useRouter } from 'vue-router'
import { useMediaStore } from '../stores/mediaStore'
import { getFileUrl } from '../config/api'

const router = useRouter()
const mediaStore = useMediaStore()

const activeFilter = ref('all')
const deleting = ref(false)
const showSuccess = ref(false)
const successMessage = ref('')

const filteredMedia = computed(() => {
  if (activeFilter.value === 'all') {
    return mediaStore.allMedia
  }
  return mediaStore.allMedia.filter(m => m.mediaType === activeFilter.value)
})

const totalCount = computed(() => mediaStore.allMedia.length)
const imageCount = computed(() => mediaStore.allMedia.filter(m => m.mediaType === 'image').length)
const videoCount = computed(() => mediaStore.allMedia.filter(m => m.mediaType === 'video').length)

function getMediaUrl(filePath) {
  if (!filePath) return '/placeholder-image.jpg'
  if (filePath.startsWith('http')) return filePath
  
  // Extract just the filename from the path
  const filename = filePath.split('\\').pop().split('/').pop()
  
  // Use the getFileUrl helper
  const url = getFileUrl(filename)
  console.log('[MediaLibraryView] getMediaUrl:', { filePath, filename, url })
  return url
}

function handleImageError(event) {
  event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23f3f4f6" width="400" height="300"/%3E%3Ctext fill="%239ca3af" font-family="sans-serif" font-size="24" dy="150" dx="50"%3EImage not found%3C/text%3E%3C/svg%3E'
}

function formatDate(dateString) {
  if (!dateString) return 'Unknown date'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

function navigateToAnnotation(media) {
  if (media.mediaType === 'image') {
    router.push(`/annotate/${media.id}`)
  } else {
    router.push(`/videos/${media.id}`)
  }
}

async function deleteMedia(media) {
  if (!confirm(`Are you sure you want to delete "${media.name}"?`)) {
    return
  }
  
  deleting.value = true
  
  try {
    await mediaStore.deleteMedia(media.id, media.mediaType)
    showSuccessToast(`"${media.name}" deleted successfully`)
  } catch (err) {
    console.error('Failed to delete media:', err)
    alert(`Failed to delete "${media.name}": ${err.message}`)
  } finally {
    deleting.value = false
  }
}

function showSuccessToast(message) {
  successMessage.value = message
  showSuccess.value = true
  setTimeout(() => {
    showSuccess.value = false
  }, 3000)
}

onMounted(async () => {
  console.log('[MediaLibraryView] Component mounted, fetching media...')
  try {
    await mediaStore.fetchMedia()
    console.log('[MediaLibraryView] Media fetched successfully:', mediaStore.allMedia.length, 'items')
  } catch (err) {
    console.error('[MediaLibraryView] Failed to load media:', err)
  }
})
</script>

<style scoped>
.library-view {
  max-width: 1400px;
  margin: 0 auto;
}

.library-header {
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

.primary-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #4F46E5;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.primary-btn:hover {
  background: #4338CA;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 32px;
  padding: 4px;
  background: white;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  width: fit-content;
}

.tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: none;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab:hover {
  color: #111827;
  background: #f9fafb;
}

.tab.active {
  background: #4F46E5;
  color: white;
}

.tab-count {
  padding: 2px 8px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.tab.active .tab-count {
  background: rgba(255, 255, 255, 0.2);
}

.loading-container {
  min-height: 400px;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.media-grid.skeleton {
  pointer-events: none;
}

.skeleton-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.skeleton-image {
  width: 100%;
  height: 200px;
  background: linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 50%, #f3f4f6 100%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-text {
  height: 16px;
  margin: 16px;
  background: linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 50%, #f3f4f6 100%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-text.short {
  width: 60%;
  height: 12px;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.media-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}

.media-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-4px);
}

.media-preview {
  position: relative;
  width: 100%;
  height: 200px;
  background: #f3f4f6;
  overflow: hidden;
}

.delete-btn {
  display: none;
}

/* ── Always-visible action bar ── */
.media-actions {
  display: flex;
  gap: 8px;
  padding: 10px 12px 12px;
  border-top: 1px dashed #d1d5db;
}

.action-annotate-btn {
  flex: 1;
  padding: 8px 10px;
  font-family: 'Patrick Hand', cursive;
  font-size: 13px;
  font-weight: 700;
  background: #fff59d;
  color: #1a1a1a;
  border: 2px solid #1a1a1a;
  border-radius: 7px;
  box-shadow: 2px 2px 0px #1a1a1a;
  cursor: pointer;
  text-align: center;
}

.action-annotate-btn:hover {
  box-shadow: 1px 1px 0px #1a1a1a;
  transform: translate(1px, 1px);
}

.action-delete-btn {
  padding: 8px 14px;
  font-family: 'Patrick Hand', cursive;
  font-size: 13px;
  font-weight: 700;
  background: #ffe0e0;
  color: #c0392b;
  border: 2px solid #1a1a1a;
  border-radius: 7px;
  box-shadow: 2px 2px 0px #1a1a1a;
  cursor: pointer;
  white-space: nowrap;
}

.action-delete-btn:hover {
  background: #ffcdd2;
  box-shadow: 1px 1px 0px #1a1a1a;
  transform: translate(1px, 1px);
}

.media-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.media-card:hover .media-preview img {
  transform: scale(1.05);
}

.video-preview {
  position: relative;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-icon {
  position: relative;
  z-index: 2;
}

.video-thumbnail {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
  opacity: 0.6;
}

.media-type-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 6px 10px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  backdrop-filter: blur(8px);
}

.media-type-badge.image {
  background: rgba(99, 102, 241, 0.9);
  color: white;
}

.media-type-badge.video {
  background: rgba(236, 72, 153, 0.9);
  color: white;
}

.media-info {
  padding: 16px;
}

.media-name {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.media-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #6b7280;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 500px;
  text-align: center;
  padding: 40px;
}

.empty-icon {
  margin-bottom: 24px;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 24px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 15px;
  color: #6b7280;
  margin: 0 0 24px 0;
}

.empty-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #4F46E5;
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
}

.empty-btn:hover {
  background: #4338CA;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 48px;
  padding: 24px;
}

.pagination-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:not(:disabled):hover {
  border-color: #4F46E5;
  color: #4F46E5;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
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

@media (max-width: 768px) {
  .library-header {
    flex-direction: column;
    gap: 16px;
  }

  .filter-tabs {
    width: 100%;
    justify-content: space-between;
  }

  .media-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 16px;
  }

  .media-preview {
    height: 140px;
  }
}
</style>