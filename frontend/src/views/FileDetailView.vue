<!-- src/views/FileDetailView.vue -->
<template>
  <div class="file-detail-view">
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
          <p class="subtitle">Image Annotation</p>
        </div>
      </div>
      <div class="header-actions">
        <button @click="saveAnnotations" class="primary-btn" :disabled="saving">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M13.3333 14V6.66667L9.33333 2.66667H3.33333C2.59695 2.66667 2 3.26362 2 4V14C2 14.7364 2.59695 15.3333 3.33333 15.3333H12C12.7364 15.3333 13.3333 14.7364 13.3333 14Z" stroke="currentColor" stroke-width="1.5"/>
            <path d="M4.66667 2.66667V6H10V2.66667" stroke="currentColor" stroke-width="1.5"/>
          </svg>
          {{ saving ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading image...</p>
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

    <!-- Main Content -->
    <div v-else class="content">
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="tool-group">
          <label class="tool-label">Label:</label>
          <input 
            v-model="currentLabel" 
            type="text" 
            placeholder="Enter label (e.g., person, car)"
            class="label-input"
            @keyup.enter="startDrawing"
          />
        </div>
        <div class="tool-group">
          <button 
            @click="mode = 'draw'" 
            :class="['tool-btn', { active: mode === 'draw' }]"
            title="Draw bounding box"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <rect x="3" y="3" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            Draw
          </button>
          <button 
            @click="mode = 'select'" 
            :class="['tool-btn', { active: mode === 'select' }]"
            title="Select annotation"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M3 3L17 10L10 11L9 18L3 3Z" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            Select
          </button>
        </div>
        <div class="tool-group">
          <button 
            @click="deleteSelected" 
            class="tool-btn danger"
            :disabled="!selectedAnnotation"
            title="Delete selected"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M3 5H17M8 9V15M12 9V15M4 5L5 17C5 17.5304 5.21071 18.0391 5.58579 18.4142C5.96086 18.7893 6.46957 19 7 19H13C13.5304 19 14.0391 18.7893 14.4142 18.4142C14.7893 18.0391 15 17.5304 15 17L16 5M7 5V3C7 2.73478 7.10536 2.48043 7.29289 2.29289C7.48043 2.10536 7.73478 2 8 2H12C12.2652 2 12.5196 2.10536 12.7071 2.29289C12.8946 2.48043 13 2.73478 13 3V5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            Delete
          </button>
          <button 
            @click="clearAll" 
            class="tool-btn"
            title="Clear all annotations"
          >
            Clear All
          </button>
        </div>
      </div>

      <!-- Canvas Container -->
      <div class="canvas-container" ref="containerRef">
        <canvas 
          ref="canvasRef"
          @mousedown="handleMouseDown"
          @mousemove="handleMouseMove"
          @mouseup="handleMouseUp"
          @mouseleave="handleMouseUp"
        ></canvas>
      </div>

      <!-- Annotations List -->
      <div class="annotations-panel">
        <h3>Annotations ({{ annotations.length }})</h3>
        <div v-if="annotations.length === 0" class="empty-annotations">
          <p>No annotations yet. Draw a bounding box to start.</p>
        </div>
        <div v-else class="annotations-list">
          <div 
            v-for="(ann, index) in annotations" 
            :key="ann.id || index"
            :class="['annotation-item', { selected: selectedAnnotation === ann }]"
            @click="selectAnnotation(ann)"
          >
            <div class="annotation-color" :style="{ background: getAnnotationColor(index) }"></div>
            <div class="annotation-info">
              <div class="annotation-label">{{ ann.label }}</div>
              <div class="annotation-coords">
                x: {{ Math.round(ann.x) }}, y: {{ Math.round(ann.y) }}, 
                w: {{ Math.round(ann.width) }}, h: {{ Math.round(ann.height) }}
              </div>
            </div>
            <button @click.stop="deleteAnnotation(ann)" class="delete-icon">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fileService } from '../services/fileService'
import { annotationService } from '../services/annotationService'
import { getFileUrl } from '../config/api'

const route = useRoute()
const router = useRouter()
const fileId = computed(() => parseInt(route.params.id))

// State
const file = ref(null)
const loading = ref(true)
const error = ref(null)
const saving = ref(false)
const showSuccess = ref(false)
const successMessage = ref('')

// Canvas refs
const canvasRef = ref(null)
const containerRef = ref(null)
const image = ref(null)

// Annotation state
const annotations = ref([])
const currentLabel = ref('object')
const mode = ref('draw') // 'draw' or 'select'
const selectedAnnotation = ref(null)

// Drawing state
const isDrawing = ref(false)
const startX = ref(0)
const startY = ref(0)
const currentBox = ref(null)

// Colors for annotations
const colors = [
  '#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6',
  '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#6366f1'
]

function getAnnotationColor(index) {
  return colors[index % colors.length]
}

async function loadFile() {
  loading.value = true
  error.value = null
  
  try {
    const response = await fileService.getFile(fileId.value)
    if (response.success && response.data && response.data.file) {
      file.value = response.data.file
      await loadImage()
      await loadAnnotations()
    } else {
      error.value = 'File not found'
    }
  } catch (err) {
    console.error('Failed to load file:', err)
    error.value = 'Failed to load file'
  } finally {
    loading.value = false
  }
}

async function loadImage() {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      image.value = img
      setupCanvas()
      resolve()
    }
    img.onerror = () => {
      error.value = 'Failed to load image'
      reject()
    }
    img.src = getFileUrl(file.value.stored_filename)
  })
}

function setupCanvas() {
  const canvas = canvasRef.value
  const container = containerRef.value
  
  if (!canvas || !image.value || !container) return
  
  // Set canvas size to fit container while maintaining aspect ratio
  const containerWidth = container.clientWidth
  const imgAspect = image.value.width / image.value.height
  
  canvas.width = containerWidth
  canvas.height = containerWidth / imgAspect
  
  drawCanvas()
}

function drawCanvas() {
  const canvas = canvasRef.value
  if (!canvas || !image.value) return
  
  const ctx = canvas.getContext('2d')
  
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // Draw image
  ctx.drawImage(image.value, 0, 0, canvas.width, canvas.height)
  
  // Draw existing annotations
  annotations.value.forEach((ann, index) => {
    const color = getAnnotationColor(index)
    const isSelected = selectedAnnotation.value === ann
    
    ctx.strokeStyle = color
    ctx.lineWidth = isSelected ? 3 : 2
    ctx.strokeRect(ann.x, ann.y, ann.width, ann.height)
    
    // Draw label
    ctx.fillStyle = color
    ctx.font = '14px Arial'
    const textWidth = ctx.measureText(ann.label).width
    ctx.fillRect(ann.x, ann.y - 20, textWidth + 8, 20)
    ctx.fillStyle = 'white'
    ctx.fillText(ann.label, ann.x + 4, ann.y - 6)
  })
  
  // Draw current box being drawn
  if (isDrawing.value && currentBox.value) {
    ctx.strokeStyle = '#4F46E5'
    ctx.lineWidth = 2
    ctx.setLineDash([5, 5])
    ctx.strokeRect(
      currentBox.value.x,
      currentBox.value.y,
      currentBox.value.width,
      currentBox.value.height
    )
    ctx.setLineDash([])
  }
}

function getMousePos(event) {
  const canvas = canvasRef.value
  const rect = canvas.getBoundingClientRect()
  return {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
}

function handleMouseDown(event) {
  const pos = getMousePos(event)
  
  if (mode.value === 'draw') {
    if (!currentLabel.value.trim()) {
      alert('Please enter a label first')
      return
    }
    isDrawing.value = true
    startX.value = pos.x
    startY.value = pos.y
    currentBox.value = { x: pos.x, y: pos.y, width: 0, height: 0 }
  } else if (mode.value === 'select') {
    // Find clicked annotation
    const clicked = annotations.value.find(ann => 
      pos.x >= ann.x && pos.x <= ann.x + ann.width &&
      pos.y >= ann.y && pos.y <= ann.y + ann.height
    )
    selectedAnnotation.value = clicked || null
    drawCanvas()
  }
}

function handleMouseMove(event) {
  if (!isDrawing.value || mode.value !== 'draw') return
  
  const pos = getMousePos(event)
  currentBox.value = {
    x: Math.min(startX.value, pos.x),
    y: Math.min(startY.value, pos.y),
    width: Math.abs(pos.x - startX.value),
    height: Math.abs(pos.y - startY.value)
  }
  drawCanvas()
}

function handleMouseUp(event) {
  if (!isDrawing.value || mode.value !== 'draw') return
  
  isDrawing.value = false
  
  if (currentBox.value && currentBox.value.width > 10 && currentBox.value.height > 10) {
    annotations.value.push({
      label: currentLabel.value.trim(),
      x: currentBox.value.x,
      y: currentBox.value.y,
      width: currentBox.value.width,
      height: currentBox.value.height,
      file_id: fileId.value
    })
    drawCanvas()
  }
  
  currentBox.value = null
}

function selectAnnotation(ann) {
  selectedAnnotation.value = ann
  mode.value = 'select'
  drawCanvas()
}

function deleteAnnotation(ann) {
  const index = annotations.value.indexOf(ann)
  if (index > -1) {
    annotations.value.splice(index, 1)
    if (selectedAnnotation.value === ann) {
      selectedAnnotation.value = null
    }
    drawCanvas()
  }
}

function deleteSelected() {
  if (selectedAnnotation.value) {
    deleteAnnotation(selectedAnnotation.value)
  }
}

function clearAll() {
  if (confirm('Are you sure you want to clear all annotations?')) {
    annotations.value = []
    selectedAnnotation.value = null
    drawCanvas()
  }
}

async function loadAnnotations() {
  try {
    const response = await annotationService.getAnnotationsByFile(fileId.value)
    if (response.success && response.data) {
      annotations.value = response.data.map(ann => ({
        ...ann,
        file_id: fileId.value
      }))
      drawCanvas()
    }
  } catch (err) {
    console.error('Failed to load annotations:', err)
  }
}

async function saveAnnotations() {
  saving.value = true
  
  try {
    // Delete all existing annotations first
    const existingIds = annotations.value.filter(a => a.id).map(a => a.id)
    for (const id of existingIds) {
      await annotationService.deleteAnnotation(id)
    }
    
    // Create new annotations
    for (const ann of annotations.value) {
      await annotationService.createAnnotation({
        file_id: fileId.value,
        label: ann.label,
        x: ann.x,
        y: ann.y,
        width: ann.width,
        height: ann.height
      })
    }
    
    showSuccessToast('Annotations saved successfully!')
    await loadAnnotations() // Reload to get IDs
  } catch (err) {
    console.error('Failed to save annotations:', err)
    alert('Failed to save annotations')
  } finally {
    saving.value = false
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

function startDrawing() {
  mode.value = 'draw'
}

// Handle window resize
function handleResize() {
  if (image.value) {
    setupCanvas()
  }
}

onMounted(() => {
  loadFile()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.file-detail-view {
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

.primary-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #4F46E5;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.primary-btn:hover:not(:disabled) {
  background: #4338CA;
}

.primary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  grid-template-columns: 1fr 300px;
  gap: 24px;
}

.toolbar {
  grid-column: 1 / -1;
  display: flex;
  gap: 16px;
  padding: 16px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  flex-wrap: wrap;
}

.tool-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.label-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  min-width: 200px;
}

.tool-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.tool-btn:hover:not(:disabled) {
  border-color: #4F46E5;
  color: #4F46E5;
}

.tool-btn.active {
  background: #4F46E5;
  color: white;
  border-color: #4F46E5;
}

.tool-btn.danger:hover:not(:disabled) {
  border-color: #ef4444;
  color: #ef4444;
}

.tool-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.canvas-container {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

canvas {
  display: block;
  cursor: crosshair;
  max-width: 100%;
}

.annotations-panel {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  height: fit-content;
  max-height: 600px;
  overflow-y: auto;
}

.annotations-panel h3 {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 16px 0;
}

.empty-annotations {
  text-align: center;
  padding: 32px 16px;
  color: #6b7280;
}

.annotations-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.annotation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.annotation-item:hover {
  border-color: #d1d5db;
  background: #f9fafb;
}

.annotation-item.selected {
  border-color: #4F46E5;
  background: #eef2ff;
}

.annotation-color {
  width: 4px;
  height: 40px;
  border-radius: 2px;
}

.annotation-info {
  flex: 1;
  min-width: 0;
}

.annotation-label {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
}

.annotation-coords {
  font-size: 12px;
  color: #6b7280;
  font-family: monospace;
}

.delete-icon {
  padding: 4px;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  transition: color 0.2s;
}

.delete-icon:hover {
  color: #ef4444;
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
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .tool-group {
    flex-wrap: wrap;
  }
}
</style>
