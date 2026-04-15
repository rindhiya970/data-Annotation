<!-- src/views/AnnotateView.vue -->
<template>
  <div class="av-page">

    <!-- ── Header bar ── -->
    <div class="av-header">
      <div class="av-header-left">
        <button class="av-back-btn" @click="goBack">← Back</button>
        <div class="av-title-block">
          <h1 class="av-title">{{ file?.original_filename || 'Loading...' }}</h1>
          <span class="av-subtitle">Image Annotation</span>
        </div>
      </div>
      <div class="av-header-right">
        <button class="av-btn av-btn-export" @click="exportDataset" title="Export YOLO dataset ZIP">
          ⬇ Export
        </button>
        <button class="av-btn av-btn-save" @click="saveAllAnnotations" :disabled="annotationStore.saving">
          {{ annotationStore.saving ? ' Saving...' : ' Save All' }}
        </button>
      </div>
    </div>

    <!-- ── Loading ── -->
    <div v-if="loading" class="av-center">
      <div class="av-spinner"></div>
      <p>Loading image...</p>
    </div>

    <!-- ── Error ── -->
    <div v-else-if="error" class="av-center av-error">
      <p>⚠️ {{ error }}</p>
      <button class="av-btn" @click="loadFile">Try Again</button>
    </div>

    <!-- ── Main workspace ── -->
    <div v-else class="av-workspace">

      <!-- LEFT: canvas column -->
      <div class="av-canvas-col">

        <!-- Toolbar -->
        <div class="av-toolbar">
          <!-- Label input -->
          <div class="av-tool-group">
            <label class="av-tool-label">Label:</label>
            <input
              v-model="currentLabel"
              type="text"
              placeholder="e.g. person, car"
              class="av-label-input"
              @keyup.enter="mode = 'draw'"
            />
          </div>

          <!-- Draw / Select -->
          <div class="av-tool-group">
            <button
              :class="['av-tool-btn', { 'av-tool-active': mode === 'draw' }]"
              @click="mode = 'draw'"
              title="Draw bounding box"
            > Draw</button>
            <button
              :class="['av-tool-btn', { 'av-tool-active': mode === 'select' }]"
              @click="mode = 'select'"
              title="Select annotation"
            >↖ Select</button>
          </div>

          <!-- AI auto-annotate -->
          <div class="av-tool-group">
            <button
              class="av-tool-btn av-ai-btn"
              @click="autoAnnotate"
              :disabled="aiLoading"
              title="Run AI auto-detection"
            >
              {{ aiLoading ? ' Detecting...' : ' Auto Annotate' }}
            </button>
            <span class="av-ai-hint">⚠️ Review before saving</span>
            <span v-if="aiError" class="av-ai-error">{{ aiError }}</span>
          </div>

          <!-- Delete selected moved to edit bar only -->
        </div>

        <!-- Edit bar (shown when annotation selected) -->
        <div v-if="annotationStore.selectedAnnotation" class="av-edit-bar">
          <span class="av-edit-label">Selected:</span>
          <input
            v-model="editLabel"
            type="text"
            class="av-label-input"
            placeholder="Edit label"
            @keyup.enter="saveEditedLabel"
          />
          <button class="av-tool-btn av-tool-active" @click="saveEditedLabel">Rename</button>
          <button class="av-tool-btn av-danger-btn" @click="deleteSelected">Delete</button>
        </div>

        <!-- Canvas paper card -->
        <div class="av-canvas-card">
          <AnnotationCanvas
            :imageUrl="imageUrl"
            :annotations="annotationStore.annotations"
            :selectedAnnotation="annotationStore.selectedAnnotation"
            :mode="mode"
            :currentLabel="currentLabel"
            @annotationCreated="handleAnnotationCreated"
            @annotationSelected="handleAnnotationSelected"
            @annotationMoved="handleAnnotationUpdate"
            @annotationResized="handleAnnotationUpdate"
          />
        </div>
      </div>

      <!-- RIGHT: annotation list sidebar -->
      <div class="av-sidebar">
        <AnnotationList
          :annotations="annotationStore.annotations"
          :selectedAnnotation="annotationStore.selectedAnnotation"
          @select="handleAnnotationSelected"
          @delete="handleAnnotationDelete"
          @clearAll="handleClearAll"
        />
      </div>
    </div>

    <!-- Toast -->
    <transition name="av-toast-anim">
      <div v-if="showSuccess" class="av-toast">
        ✅ {{ successMessage }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fileService } from '../services/fileService'
import { useAnnotationStore } from '../stores/annotationStore'
import { getFileUrl } from '../config/api'
import AnnotationCanvas from '../components/annotation/AnnotationCanvas.vue'
import AnnotationList from '../components/annotation/AnnotationList.vue'

const route = useRoute()
const router = useRouter()
const annotationStore = useAnnotationStore()

const fileId = computed(() => parseInt(route.params.id))

// State
const file = ref(null)
const loading = ref(true)
const error = ref(null)
const showSuccess = ref(false)
const successMessage = ref('')

// Annotation state
const currentLabel = ref('object')
const mode = ref('draw') // 'draw' or 'select'
const editLabel = ref('')

// ── AI auto-annotate state ──
const aiLoading = ref(false)
const aiError   = ref('')

async function autoAnnotate() {
  aiError.value   = ''
  aiLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const res   = await fetch(
      `http://127.0.0.1:5000/api/annotations/auto-annotate/${fileId.value}`,
      { method: 'POST', headers: { Authorization: `Bearer ${token}` } }
    )
    const json = await res.json()
    if (!res.ok || !json.success) {
      aiError.value = json.message || 'Auto-annotation failed'
      return
    }
    // Map AI detections → store format and APPEND (never overwrite)
    // Filter out low-confidence predictions (< 0.5)
    const CONF_THRESHOLD = 0.5
    const filtered = json.data.filter(det => det.confidence >= CONF_THRESHOLD)
    const skipped  = json.data.length - filtered.length

    const aiAnnotations = filtered.map((det, i) => ({
      id:         `ai_${Date.now()}_${i}`,
      label:      `${det.label} (${(det.confidence * 100).toFixed(0)}%)`,
      x:          det.x,
      y:          det.y,
      width:      det.width,
      height:     det.height,
      confidence: det.confidence,
      ai:         true,
    }))
    annotationStore.annotations.push(...aiAnnotations)
    const msg = skipped > 0
      ? `${aiAnnotations.length} detection(s) added (${skipped} low-confidence skipped) — review and save`
      : `${aiAnnotations.length} AI detection(s) added — review and save`
    showSuccessToast(msg)
  } catch (e) {
    aiError.value = 'Request failed. Is the server running?'
  } finally {
    aiLoading.value = false
  }
}

// Computed
const imageUrl = computed(() => {
  if (!file.value) return ''
  return getFileUrl(file.value.stored_filename)
})

// Load file metadata
async function loadFile() {
  loading.value = true
  error.value = null
  
  try {
    const response = await fileService.getFile(fileId.value)
    
    if (response.success && response.data && response.data.file) {
      file.value = response.data.file
      
      // Load existing annotations
      await annotationStore.fetchAnnotations(fileId.value)
    } else {
      error.value = 'File not found'
    }
  } catch (err) {
    console.error('Failed to load file:', err)
    error.value = err.response?.data?.message || 'Failed to load file'
  } finally {
    loading.value = false
  }
}

// Handle annotation created from canvas
async function handleAnnotationCreated(annotationData) {
  try {
    await annotationStore.createAnnotation({
      ...annotationData,
      file_id: fileId.value
    })
    
    showSuccessToast('Annotation created')
  } catch (err) {
    console.error('Failed to create annotation:', err)
    alert(annotationStore.error || 'Failed to create annotation')
  }
}

// Handle annotation selection
function handleAnnotationSelected(annotation) {
  annotationStore.selectAnnotation(annotation)
  if (annotation) {
    editLabel.value = annotation.label
    mode.value = 'select'
  }
}

// Handle move/resize from canvas - save to backend
async function handleAnnotationUpdate(data) {
  try {
    await annotationStore.updateAnnotation(data.id, data)
    showSuccessToast('Annotation updated')
  } catch (err) {
    console.error('Failed to update annotation:', err)
  }
}

// Save edited label for selected annotation
async function saveEditedLabel() {
  if (!annotationStore.selectedAnnotation || !editLabel.value.trim()) return
  try {
    await annotationStore.updateAnnotation(annotationStore.selectedAnnotation.id, { label: editLabel.value.trim() })
    showSuccessToast('Label updated')
  } catch (err) {
    console.error('Failed to update label:', err)
  }
}

// Delete selected annotation
async function deleteSelected() {
  if (!annotationStore.selectedAnnotation) return
  
  await handleAnnotationDelete(annotationStore.selectedAnnotation)
}

// Handle annotation deletion
async function handleAnnotationDelete(annotation) {
  if (!confirm(`Delete annotation "${annotation.label}"?`)) return
  
  try {
    // AI annotations with temp ids (ai_...) are not in DB — remove from local state only
    if (typeof annotation.id === 'string' && annotation.id.startsWith('ai_')) {
      const idx = annotationStore.annotations.findIndex(a => a.id === annotation.id)
      if (idx !== -1) annotationStore.annotations.splice(idx, 1)
      if (annotationStore.selectedAnnotation?.id === annotation.id) {
        annotationStore.selectAnnotation(null)
      }
      showSuccessToast('Annotation removed')
      return
    }
    await annotationStore.deleteAnnotation(annotation.id)
    showSuccessToast('Annotation deleted')
  } catch (err) {
    console.error('Failed to delete annotation:', err)
    alert(annotationStore.error || 'Failed to delete annotation')
  }
}

// Clear all annotations
async function handleClearAll() {
  if (!confirm('Delete all annotations? This cannot be undone.')) return
  
  try {
    const all = [...annotationStore.annotations]
    for (const ann of all) {
      if (typeof ann.id === 'string' && ann.id.startsWith('ai_')) {
        // Temp AI annotation — remove from local state only
        const idx = annotationStore.annotations.findIndex(a => a.id === ann.id)
        if (idx !== -1) annotationStore.annotations.splice(idx, 1)
      } else {
        await annotationStore.deleteAnnotation(ann.id)
      }
    }
    showSuccessToast('All annotations cleared')
  } catch (err) {
    console.error('Failed to clear annotations:', err)
    alert('Failed to clear all annotations')
  }
}

// Save all annotations - persists any unsaved AI annotations to backend
async function saveAllAnnotations() {
  try {
    const unsaved = annotationStore.annotations.filter(
      a => typeof a.id === 'string' && a.id.startsWith('ai_')
    )

    if (unsaved.length > 0) {
      const token = localStorage.getItem('token')
      for (const ann of unsaved) {
        // Use fetch directly to avoid createAnnotation() double-pushing into the store
        const res = await fetch('http://127.0.0.1:5000/api/annotations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({
            file_id: fileId.value,
            label:   ann.label,
            x:       ann.x,
            y:       ann.y,
            width:   ann.width,
            height:  ann.height
          })
        })
        const json = await res.json()
        if (json.success && json.data) {
          // Replace temp entry with real DB record in-place
          const idx = annotationStore.annotations.findIndex(a => a.id === ann.id)
          if (idx !== -1) annotationStore.annotations.splice(idx, 1, json.data)
        }
      }
      showSuccessToast(`${unsaved.length} AI annotation(s) saved`)
    } else {
      showSuccessToast('All annotations already saved')
    }
  } catch (err) {
    console.error('Failed to save annotations:', err)
    alert('Failed to save annotations')
  }
}

// Show success toast
function showSuccessToast(message) {
  successMessage.value = message
  showSuccess.value = true
  setTimeout(() => {
    showSuccess.value = false
  }, 3000)
}

// Export YOLO dataset
async function exportDataset() {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://127.0.0.1:5000/api/export/yolo/dataset', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!response.ok) {
      const err = await response.json()
      alert(err.message || 'Export failed')
      return
    }
    const blob = await response.blob()
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = 'yolo_dataset.zip'
    a.click()
    URL.revokeObjectURL(url)
    showSuccessToast('Dataset exported!')
  } catch (err) {
    console.error('Export error:', err)
    alert('Export failed')
  }
}

// Navigate back
function goBack() {
  router.push('/media/library')
}

// Lifecycle
onMounted(() => {
  loadFile()
})
</script>

<style scoped>
/* ── Page ── */
.av-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  font-family: 'Patrick Hand', cursive;
  background: #fffef5;
  color: #1a1a1a;
}

/* ══════════════════════════════
   HEADER
══════════════════════════════ */
.av-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding: 14px 20px;
  background: #fffef5;
  border-bottom: 2px dashed #1a1a1a;
  flex-shrink: 0;
}

.av-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.av-back-btn {
  padding: 7px 14px;
  font-family: 'Patrick Hand', cursive;
  font-size: 14px;
  background: #fff;
  border: 2px solid #1a1a1a;
  border-radius: 8px;
  box-shadow: 3px 3px 0px #1a1a1a;
  cursor: pointer;
  color: #1a1a1a;
}

.av-back-btn:hover {
  box-shadow: 1px 1px 0px #1a1a1a;
  transform: translate(2px, 2px);
}

.av-title-block {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.av-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  /* yellow marker highlight */
  background: linear-gradient(104deg, transparent 0.5%, #fff59d 2%, #fff59d 95%, transparent 99%);
  padding: 1px 8px;
  border-radius: 3px;
  display: inline-block;
}

.av-subtitle {
  font-size: 12px;
  color: #666;
  padding-left: 4px;
}

.av-header-right {
  display: flex;
  gap: 10px;
}

/* ══════════════════════════════
   SHARED BUTTON BASE
══════════════════════════════ */
.av-btn {
  font-family: 'Patrick Hand', cursive;
  font-size: 14px;
  padding: 8px 18px;
  background: #fff;
  color: #1a1a1a;
  border: 2px solid #1a1a1a;
  border-radius: 8px;
  box-shadow: 3px 3px 0px #1a1a1a;
  cursor: pointer;
}

.av-btn:hover:not(:disabled) {
  box-shadow: 1px 1px 0px #1a1a1a;
  transform: translate(2px, 2px);
}

.av-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  box-shadow: none;
}

.av-btn-save {
  background: #fff59d;
  font-weight: 700;
}

.av-btn-export {
  background: #fff;
}

/* ══════════════════════════════
   LOADING / ERROR
══════════════════════════════ */
.av-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  font-family: 'Patrick Hand', cursive;
}

.av-error { color: #c0392b; }

.av-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #ddd;
  border-top-color: #1a1a1a;
  border-radius: 50%;
  animation: av-spin 0.9s linear infinite;
}

@keyframes av-spin { to { transform: rotate(360deg); } }

/* ══════════════════════════════
   WORKSPACE  (canvas + sidebar)
══════════════════════════════ */
.av-workspace {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 0;
  flex: 1;
  overflow: hidden;
}

/* ── Canvas column ── */
.av-canvas-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  overflow: hidden;
}

/* ── Toolbar ── */
.av-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding: 10px 14px;
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 10px;
  box-shadow: 3px 3px 0px #1a1a1a;
  flex-shrink: 0;
}

.av-tool-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.av-tool-label {
  font-size: 13px;
  font-weight: 700;
  color: #1a1a1a;
  font-family: 'Patrick Hand', cursive;
}

.av-label-input {
  padding: 6px 10px;
  font-family: 'Patrick Hand', cursive;
  font-size: 13px;
  background: #fffef5;
  border: 2px dashed #1a1a1a;
  border-radius: 6px;
  color: #1a1a1a;
  min-width: 150px;
  outline: none;
  box-shadow: none;
}

.av-label-input:focus {
  border-style: solid;
  background: #fff;
}

.av-tool-btn {
  padding: 6px 12px;
  font-family: 'Patrick Hand', cursive;
  font-size: 13px;
  background: #fff;
  color: #1a1a1a;
  border: 2px solid #1a1a1a;
  border-radius: 7px;
  box-shadow: 2px 2px 0px #1a1a1a;
  cursor: pointer;
}

.av-tool-btn:hover:not(:disabled) {
  box-shadow: 1px 1px 0px #1a1a1a;
  transform: translate(1px, 1px);
}

.av-tool-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  box-shadow: none;
}

/* Active tool = yellow highlight */
.av-tool-active {
  background: #fff59d !important;
  font-weight: 700;
}

/* AI button */
.av-ai-btn {
  background: #e8f5e9;
  border-color: #1a1a1a;
}

.av-ai-btn:hover:not(:disabled) {
  background: #c8e6c9;
}

/* Danger button */
.av-danger-btn:hover:not(:disabled) {
  background: #fce4ec;
  border-color: #c0392b;
  color: #c0392b;
}

.av-ai-error {
  font-size: 12px;
  color: #c0392b;
  font-family: 'Patrick Hand', cursive;
}

.av-ai-hint {
  font-size: 11px;
  color: #b45309;
  font-family: 'Patrick Hand', cursive;
  font-style: italic;
}

/* ── Edit bar ── */
.av-edit-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 8px 12px;
  background: #fffde7;
  border: 2px solid #1a1a1a;
  border-radius: 8px;
  box-shadow: 2px 2px 0px #1a1a1a;
  flex-shrink: 0;
}

.av-edit-label {
  font-size: 13px;
  font-weight: 700;
  color: #1a1a1a;
  font-family: 'Patrick Hand', cursive;
}

/* ── Canvas paper card ── */
.av-canvas-card {
  flex: 1;
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 12px;
  box-shadow: 4px 4px 0px #1a1a1a;
  padding: 8px;
  transform: rotate(-0.2deg);
  overflow: hidden;
  min-height: 0;
}

/* ── Sidebar ── */
.av-sidebar {
  border-left: 2px dashed #1a1a1a;
  background: #fffef5;
  overflow-y: auto;
  padding: 16px 12px;
}

/* ══════════════════════════════
   TOAST
══════════════════════════════ */
.av-toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 20px;
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 10px;
  box-shadow: 4px 4px 0px #1a1a1a;
  font-family: 'Patrick Hand', cursive;
  font-size: 14px;
  font-weight: 700;
  color: #1a1a1a;
  z-index: 1000;
}

.av-toast-anim-enter-active,
.av-toast-anim-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.av-toast-anim-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.av-toast-anim-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .av-workspace {
    grid-template-columns: 1fr;
  }
  .av-sidebar {
    border-left: none;
    border-top: 2px dashed #1a1a1a;
    max-height: 280px;
  }
}

@media (max-width: 600px) {
  .av-header {
    padding: 10px 14px;
  }
  .av-title {
    font-size: 0.95rem;
  }
}
</style>
