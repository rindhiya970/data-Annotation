<!-- src/views/ProjectsView.vue -->
<template>
  <div class="pv">
    <div class="pv-header">
      <div>
        <h2 class="pv-title">Annotated Files</h2>
        <p class="pv-sub">Files you have annotated — click to continue annotating</p>
      </div>
      <button class="pv-upload-btn" @click="$router.push('/media/upload')">
        + Upload New
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="pv-center">
      <div class="pv-spinner"></div>
      <p>Loading annotated files...</p>
    </div>

    <!-- Empty -->
    <div v-else-if="files.length === 0" class="pv-empty">
      <div class="pv-empty-icon">📂</div>
      <h3>No annotated files yet</h3>
      <p>Upload an image or video and start annotating to see it here.</p>
      <button class="pv-upload-btn" @click="$router.push('/media/upload')">
        Upload &amp; Annotate
      </button>
    </div>

    <!-- Grid -->
    <div v-else class="pv-grid">
      <div
        v-for="file in files"
        :key="file.id"
        class="pv-card"
        @click="openAnnotation(file)"
        :title="`Continue annotating ${file.original_filename}`"
      >
        <!-- Thumbnail -->
        <div class="pv-thumb">
          <img
            v-if="file.file_type === 'image'"
            :src="getFileUrl(file.stored_filename)"
            :alt="file.original_filename"
            @error="onImgError"
          />
          <div v-else class="pv-video-thumb">
            <svg width="36" height="36" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="20" fill="rgba(0,0,0,0.15)"/>
              <path d="M20 16L32 24L20 32V16Z" fill="white"/>
            </svg>
          </div>
          <!-- Type badge -->
          <span class="pv-type-badge" :class="file.file_type">
            {{ file.file_type === 'image' ? '🖼' : '🎬' }}
          </span>
        </div>

        <!-- Info -->
        <div class="pv-info">
          <h3 class="pv-filename">{{ file.original_filename }}</h3>
          <div class="pv-meta">
            <span class="pv-count">
              {{ file.annotation_count }} annotation{{ file.annotation_count !== 1 ? 's' : '' }}
            </span>
            <span class="pv-date">{{ formatDate(file.created_at) }}</span>
          </div>
          <!-- Progress bar: annotations as a visual indicator -->
          <div class="pv-bar-wrap">
            <div
              class="pv-bar-fill"
              :style="{ width: Math.min(file.annotation_count * 5, 100) + '%' }"
            ></div>
          </div>
          <div class="pv-card-actions">
            <button class="pv-continue-btn" @click.stop="openAnnotation(file)">
              {{ file.file_type === 'image' ? '✏️ Continue Annotating' : '🎬 Annotate Frames' }}
            </button>
            <button class="pv-delete-btn" @click.stop="deleteFile(file)" title="Delete this file and its annotations">
              🗑
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getFileUrl } from '../config/api'

const router = useRouter()
const files = ref([])
const loading = ref(true)

async function fetchAnnotatedFiles() {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('http://127.0.0.1:5000/api/files/annotated', {
      headers: { Authorization: `Bearer ${token}` }
    })
    const json = await res.json()
    if (json.success) {
      files.value = json.data.files
    }
  } catch (e) {
    console.error('Failed to fetch annotated files', e)
  } finally {
    loading.value = false
  }
}

function openAnnotation(file) {
  if (file.file_type === 'image') {
    router.push(`/annotate/${file.id}`)
  } else {
    router.push(`/videos/${file.id}`)
  }
}

async function deleteFile(file) {
  if (!confirm(`Delete "${file.original_filename}" and all its annotations?`)) return
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`http://127.0.0.1:5000/api/files/${file.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    })
    const json = await res.json()
    if (json.success) {
      files.value = files.value.filter(f => f.id !== file.id)
    } else {
      alert(json.message || 'Delete failed')
    }
  } catch (e) {
    console.error('Delete failed', e)
    alert('Delete failed')
  }
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function onImgError(e) {
  e.target.style.display = 'none'
  e.target.parentElement.classList.add('pv-img-error')
}

onMounted(fetchAnnotatedFiles)
</script>

<style scoped>
.pv {
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Patrick Hand', cursive;
}

/* ── Header ── */
.pv-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 12px;
}

.pv-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 6px 0;
  background: linear-gradient(104deg, transparent 0.5%, #fff59d 2%, #fff59d 95%, transparent 99%);
  padding: 2px 8px;
  border-radius: 3px;
  display: inline-block;
}

.pv-sub {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}

.pv-upload-btn {
  padding: 10px 20px;
  font-family: 'Patrick Hand', cursive;
  font-size: 14px;
  font-weight: 700;
  background: #1a1a1a;
  color: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 8px;
  box-shadow: 3px 3px 0px #4f46e5;
  cursor: pointer;
}

.pv-upload-btn:hover {
  box-shadow: 5px 5px 0px #4f46e5;
  transform: translate(-1px, -1px);
}

/* ── Loading ── */
.pv-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 80px 0;
  color: #666;
}

.pv-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #ddd;
  border-top-color: #1a1a1a;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Empty ── */
.pv-empty {
  text-align: center;
  padding: 80px 24px;
  border: 2px dashed #ccc;
  border-radius: 12px;
  background: #fffef5;
}

.pv-empty-icon { font-size: 3rem; margin-bottom: 16px; }
.pv-empty h3 { font-size: 1.2rem; font-weight: 700; margin: 0 0 8px; color: #1a1a1a; }
.pv-empty p { font-size: 0.9rem; color: #666; margin: 0 0 24px; }

/* ── Grid ── */
.pv-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

/* ── Card ── */
.pv-card {
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 10px;
  box-shadow: 4px 4px 0px #1a1a1a;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.12s, transform 0.12s;
  display: flex;
  flex-direction: column;
}

.pv-card:hover {
  box-shadow: 6px 6px 0px #1a1a1a;
  transform: translate(-1px, -1px);
}

/* Thumbnail */
.pv-thumb {
  position: relative;
  height: 160px;
  background: #f0ede4;
  overflow: hidden;
}

.pv-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.pv-thumb.pv-img-error {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: #ccc;
}

.pv-video-thumb {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #2d2d2d, #555);
  display: flex;
  align-items: center;
  justify-content: center;
}

.pv-type-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #fffef5;
  border: 1.5px solid #1a1a1a;
  border-radius: 6px;
  padding: 2px 7px;
  font-size: 13px;
  box-shadow: 1px 1px 0px #1a1a1a;
}

/* Info section */
.pv-info {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.pv-filename {
  font-size: 0.95rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pv-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #666;
}

.pv-count {
  font-weight: 700;
  color: #4f46e5;
}

/* Progress bar */
.pv-bar-wrap {
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  border: 1px solid #ccc;
  overflow: hidden;
}

.pv-bar-fill {
  height: 100%;
  background: #fff59d;
  border-right: 2px solid #1a1a1a;
  transition: width 0.3s ease;
  min-width: 8px;
}

.pv-continue-btn {
  padding: 6px 14px;
  font-family: 'Patrick Hand', cursive;
  font-size: 12px;
  font-weight: 700;
  background: #fff59d;
  color: #1a1a1a;
  border: 1.5px solid #1a1a1a;
  border-radius: 6px;
  box-shadow: 2px 2px 0px #1a1a1a;
  cursor: pointer;
  flex: 1;
}

.pv-continue-btn:hover {
  box-shadow: 1px 1px 0px #1a1a1a;
  transform: translate(1px, 1px);
}

.pv-card-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 4px;
}

.pv-delete-btn {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  background: #ffe0e0;
  color: #c0392b;
  border: 1.5px solid #1a1a1a;
  border-radius: 6px;
  box-shadow: 2px 2px 0px #1a1a1a;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.pv-delete-btn:hover {
  background: #ffcdd2;
  box-shadow: 1px 1px 0px #1a1a1a;
  transform: translate(1px, 1px);
}

@media (max-width: 600px) {
  .pv-grid {
    grid-template-columns: 1fr;
  }
}
</style>
