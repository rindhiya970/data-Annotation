<template>
  <div class="va-view">
    <!-- Header -->
    <div class="va-header">
      <button @click="$router.push(`/videos/${fileId}`)" class="back-btn">← Back</button>
      <div>
        <h1 class="va-title">{{ filename }}</h1>
        <span class="va-sub">Video Annotation — Frame {{ currentFrameNumber }} / {{ frames.length }}</span>
      </div>
      <button @click="exportDataset" class="export-btn">⬇ Export Dataset</button>
    </div>

    <div v-if="loading" class="center-msg"><div class="spinner"></div><p>Loading frames...</p></div>
    <div v-else-if="error" class="center-msg error-msg">{{ error }}</div>

    <div v-else class="va-body">
      <!-- Left: Canvas -->
      <div class="va-canvas-col">
        <!-- Toolbar -->
        <div class="va-toolbar">
          <label>Label:</label>
          <input v-model="currentLabel" class="label-input" placeholder="e.g. person, car" />
          <button :class="['tool-btn', { active: mode==='draw' }]" @click="mode='draw'">✏ Draw</button>
          <button :class="['tool-btn', { active: mode==='select' }]" @click="mode='select'">↖ Select</button>
          <button class="tool-btn ai-btn" @click="autoAnnotateFrame" :disabled="aiLoading || !currentFrame">
            <span v-if="aiLoading" class="ai-spin"></span>
            <span v-else>🤖</span>
            {{ aiLoading ? 'Detecting...' : 'Auto Annotate Frame' }}
          </button>
          <span class="ai-hint-text">⚠️ Review before saving</span>
          <span v-if="aiMsg" :class="['ai-msg', aiMsg.includes('detected') && !aiMsg.includes('No') ? 'ai-ok' : 'ai-warn']">
            {{ aiMsg }}
          </span>
          <span class="divider">|</span>
          <button class="tool-btn" @click="prevFrame" :disabled="currentFrameIdx===0">‹ Prev</button>
          <span class="frame-counter">{{ currentFrameIdx+1 }} / {{ frames.length }}</span>
          <button class="tool-btn" @click="nextFrame" :disabled="currentFrameIdx===frames.length-1">Next ›</button>
        </div>

        <!-- Selected annotation edit bar -->
        <div v-if="annotationStore.selectedAnnotation" class="edit-bar">
          <span class="edit-label">Selected:</span>
          <input v-model="editLabel" class="label-input" placeholder="Edit label" @keyup.enter="saveLabel" />
          <button class="tool-btn active" @click="saveLabel">Rename</button>
          <button class="tool-btn danger" @click="deleteSelected">Delete</button>
        </div>

        <!-- Canvas -->
        <AnnotationCanvas
          v-if="currentFrameUrl"
          :imageUrl="currentFrameUrl"
          :annotations="annotationStore.annotations"
          :selectedAnnotation="annotationStore.selectedAnnotation"
          :mode="mode"
          :currentLabel="currentLabel"
          @annotationCreated="handleCreated"
          @annotationSelected="handleSelected"
          @annotationMoved="handleUpdate"
          @annotationResized="handleUpdate"
        />
        <div v-else class="no-frame">No frame available</div>

        <!-- Frame scrubber -->
        <div class="scrubber">
          <input type="range" min="0" :max="frames.length-1" v-model.number="currentFrameIdx"
                 @change="jumpToFrame(currentFrameIdx)" class="scrubber-range" />
        </div>

        <!-- Frame thumbnails strip -->
        <div class="thumb-strip" ref="thumbStrip">
          <div
            v-for="(frame, idx) in frames"
            :key="frame.id"
            :class="['thumb', { active: idx === currentFrameIdx }]"
            @click="jumpToFrame(idx)"
          >
            <img :src="frameUrl(frame.id)" loading="lazy" />
            <span class="thumb-num">{{ frame.frame_number }}</span>
            <span v-if="frameCounts[String(frame.id)]" class="thumb-badge">{{ frameCounts[String(frame.id)] }}</span>
          </div>
        </div>
      </div>

      <!-- Right: Annotation list -->
      <div class="va-sidebar">
        <AnnotationList
          :annotations="annotationStore.annotations"
          :selectedAnnotation="annotationStore.selectedAnnotation"
          @select="handleSelected"
          @delete="handleDelete"
          @clearAll="handleClearAll"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAnnotationStore } from '../stores/annotationStore'
import AnnotationCanvas from '../components/annotation/AnnotationCanvas.vue'
import AnnotationList from '../components/annotation/AnnotationList.vue'

const route  = useRoute()
const router = useRouter()
const annotationStore = useAnnotationStore()

const fileId  = computed(() => parseInt(route.params.id))
const token   = () => localStorage.getItem('token')
const BASE    = 'http://127.0.0.1:5000'

const loading  = ref(true)
const error    = ref(null)
const filename = ref('')
const frames   = ref([])
const videoId  = ref(null)

const currentFrameIdx = ref(0)
const currentLabel    = ref('object')
const editLabel       = ref('')
const mode            = ref('draw')
const frameCounts     = ref({})  // frame_id → annotation count

// ── AI auto-annotate state ─────────────────────────────────
const aiLoading = ref(false)
const aiMsg     = ref('')   // success/error feedback

async function autoAnnotateFrame() {
  if (!currentFrame.value) return
  aiMsg.value     = ''
  aiLoading.value = true
  try {
    const res  = await fetch(`${BASE}/api/annotations/auto-annotate-frame/${currentFrame.value.id}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token()}` }
    })
    const json = await res.json()
    if (!res.ok || !json.success) {
      aiMsg.value = json.message || 'Auto-annotation failed'
      return
    }
    if (json.count === 0) {
      aiMsg.value = 'No objects detected'
      return
    }
    // Append AI detections — never overwrite existing annotations
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
    const skipNote = skipped > 0 ? `, ${skipped} low-confidence skipped` : ''
    aiMsg.value = `${aiAnnotations.length} object(s) detected${skipNote} — review and save`
    // Update badge optimistically
    const key = String(currentFrame.value.id)
    frameCounts.value[key] = annotationStore.annotations.length
  } catch {
    aiMsg.value = 'Request failed. Is the server running?'
  } finally {
    aiLoading.value = false
    setTimeout(() => { aiMsg.value = '' }, 4000)
  }
}

const currentFrame = computed(() => frames.value[currentFrameIdx.value] || null)
const currentFrameNumber = computed(() => currentFrame.value?.frame_number ?? 0)
const currentFrameUrl    = computed(() => currentFrame.value ? frameUrl(currentFrame.value.id) : '')

function frameUrl(frameId) {
  return `${BASE}/api/videos/frame-image/${frameId}?token=${token()}`
}

// ── Load video + frames ────────────────────────────────────
async function loadVideo() {
  loading.value = true
  error.value   = null
  try {
    const res  = await fetch(`${BASE}/api/videos/by-file/${fileId.value}`, {
      headers: { Authorization: `Bearer ${token()}` }
    })
    const data = await res.json()
    if (!data.success) { error.value = data.message; return }
    videoId.value  = data.data.video.id
    filename.value = data.data.video.filename
    frames.value   = data.data.frames
    if (frames.value.length) await loadFrameAnnotations()
  } catch (e) {
    error.value = 'Failed to load video data'
  } finally {
    loading.value = false
  }
}

async function loadFrameAnnotations() {
  if (!currentFrame.value) return
  annotationStore.clearAnnotations()
  try {
    const res  = await fetch(`${BASE}/api/annotations/frame/${currentFrame.value.id}`, {
      headers: { Authorization: `Bearer ${token()}` }
    })
    const data = await res.json()
    if (data.success) {
      annotationStore.annotations.splice(0, annotationStore.annotations.length, ...data.data)
    }
  } catch (e) {
    console.error('Failed to load frame annotations', e)
  }
}

async function refreshFrameCounts() {
  if (!videoId.value) return
  try {
    const res  = await fetch(`${BASE}/api/annotations/video/${videoId.value}/frame-counts`, {
      headers: { Authorization: `Bearer ${token()}` }
    })
    const data = await res.json()
    if (data.success) frameCounts.value = data.data
  } catch (e) {
    console.error('Failed to load frame counts', e)
  }
}

// ── Flush unsaved (AI) annotations to DB before leaving a frame ───
// Only annotations with a temp string id (ai_...) need saving.
// Already-saved annotations have numeric ids from the DB.
async function flushUnsaved() {
  if (!currentFrame.value) return
  const unsaved = annotationStore.annotations.filter(a => typeof a.id === 'string' && a.id.startsWith('ai_'))
  if (!unsaved.length) return
  for (const ann of unsaved) {
    try {
      // Save directly via fetch to avoid the store's push() causing duplicates
      const res = await fetch(`${BASE}/api/annotations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token()}`
        },
        body: JSON.stringify({
          label:    ann.label,
          x:        ann.x,
          y:        ann.y,
          width:    ann.width,
          height:   ann.height,
          frame_id: currentFrame.value.id,
          video_id: videoId.value
        })
      })
      const json = await res.json()
      if (json.success && json.data) {
        // Replace temp entry with the real DB record in-place
        const idx = annotationStore.annotations.findIndex(a => a.id === ann.id)
        if (idx !== -1) annotationStore.annotations.splice(idx, 1, json.data)
      }
    } catch (e) {
      console.error('Failed to save AI annotation', e)
    }
  }
  // Update badge count for this frame
  const key = String(currentFrame.value.id)
  frameCounts.value[key] = annotationStore.annotations.length
}

// ── Navigation ─────────────────────────────────────────────
async function prevFrame() {
  if (currentFrameIdx.value > 0) {
    await flushUnsaved()
    currentFrameIdx.value--
    await loadFrameAnnotations()
  }
}
async function nextFrame() {
  if (currentFrameIdx.value < frames.value.length - 1) {
    await flushUnsaved()
    currentFrameIdx.value++
    await loadFrameAnnotations()
  }
}
async function jumpToFrame(idx) {
  await flushUnsaved()
  currentFrameIdx.value = idx
  await loadFrameAnnotations()
}

// ── Annotation handlers ────────────────────────────────────
async function handleCreated(data) {
  try {
    await annotationStore.createAnnotation({
      ...data,
      frame_id: currentFrame.value.id,
      video_id: videoId.value
    })
    const key = String(currentFrame.value.id)
    frameCounts.value[key] = (frameCounts.value[key] || 0) + 1
  } catch (e) {
    alert(annotationStore.error || 'Failed to create annotation')
  }
}

function handleSelected(ann) {
  annotationStore.selectAnnotation(ann)
  if (ann) { editLabel.value = ann.label; mode.value = 'select' }
}

async function handleUpdate(data) {
  try { await annotationStore.updateAnnotation(data.id, data) } catch {}
}

async function saveLabel() {
  if (!annotationStore.selectedAnnotation || !editLabel.value.trim()) return
  await annotationStore.updateAnnotation(annotationStore.selectedAnnotation.id, { label: editLabel.value.trim() })
}

async function deleteSelected() {
  if (!annotationStore.selectedAnnotation) return
  await handleDelete(annotationStore.selectedAnnotation)
}

async function handleDelete(ann) {
  if (!confirm(`Delete "${ann.label}"?`)) return
  await annotationStore.deleteAnnotation(ann.id)
  const key = String(currentFrame.value.id)
  if (frameCounts.value[key] > 0) frameCounts.value[key]--
}

async function handleClearAll() {
  if (!confirm('Delete all annotations on this frame?')) return
  const all = [...annotationStore.annotations]
  for (const ann of all) {
    if (typeof ann.id === 'string' && ann.id.startsWith('ai_')) {
      // Unsaved temp annotation — just remove from local state
      const idx = annotationStore.annotations.findIndex(a => a.id === ann.id)
      if (idx !== -1) annotationStore.annotations.splice(idx, 1)
    } else {
      await annotationStore.deleteAnnotation(ann.id)
    }
  }
  frameCounts.value[String(currentFrame.value.id)] = 0
}

// ── Export ─────────────────────────────────────────────────
async function exportDataset() {
  if (!videoId.value) { alert('Video not loaded yet'); return }
  try {
    const res = await fetch(`${BASE}/api/export/yolo/video/${videoId.value}`, {
      headers: { Authorization: `Bearer ${token()}` }
    })
    if (!res.ok) { const e = await res.json(); alert(e.message || 'Export failed'); return }
    const blob = await res.blob()
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href = url; a.download = `video_${videoId.value}_yolo.zip`; a.click()
    URL.revokeObjectURL(url)
  } catch { alert('Export failed') }
}

// ── Keyboard shortcuts ─────────────────────────────────────
function onKey(e) {
  if (e.target.tagName === 'INPUT') return
  if (e.key === 'ArrowRight') nextFrame()
  if (e.key === 'ArrowLeft')  prevFrame()
}

onMounted(async () => {
  await loadVideo()
  window.addEventListener('keydown', onKey)
  // Refresh counts in background after load (non-blocking)
  refreshFrameCounts()
})
</script>

<style scoped>
.va-view { max-width: 1600px; margin: 0 auto; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
.va-header { display: flex; align-items: center; gap: 16px; padding: 12px 20px; border-bottom: 1px solid #e5e7eb; background: #fff; flex-shrink: 0; }
.va-title { font-size: 18px; font-weight: 600; margin: 0; }
.va-sub { font-size: 12px; color: #6b7280; }
.back-btn { padding: 7px 14px; border: 1px solid #d1d5db; border-radius: 6px; background: #fff; cursor: pointer; }
.back-btn:hover { border-color: #4F46E5; color: #4F46E5; }
.export-btn { margin-left: auto; padding: 8px 16px; background: #4F46E5; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
.export-btn:hover { background: #4338CA; }
.center-msg { display: flex; flex-direction: column; align-items: center; justify-content: center; flex: 1; gap: 12px; }
.error-msg { color: #ef4444; }
.spinner { width: 40px; height: 40px; border: 4px solid #e5e7eb; border-top-color: #4F46E5; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.va-body { display: grid; grid-template-columns: 1fr 300px; gap: 16px; padding: 16px; flex: 1; overflow: hidden; }
.va-canvas-col { display: flex; flex-direction: column; gap: 8px; overflow: hidden; }
.va-sidebar { overflow-y: auto; }

.va-toolbar { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding: 8px 12px; background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; flex-shrink: 0; }
.va-toolbar label { font-size: 13px; font-weight: 500; color: #374151; }
.label-input { padding: 6px 10px; border: 1px solid #d1d5db; border-radius: 5px; font-size: 13px; min-width: 140px; }
.tool-btn { padding: 6px 12px; border: 1px solid #d1d5db; border-radius: 5px; background: #fff; cursor: pointer; font-size: 13px; }
.tool-btn:hover:not(:disabled) { border-color: #4F46E5; color: #4F46E5; }
.tool-btn.active { background: #4F46E5; color: #fff; border-color: #4F46E5; }
.tool-btn.danger:hover { border-color: #ef4444; color: #ef4444; }
.tool-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.divider { color: #d1d5db; }

/* ── AI button ── */
.ai-btn { background: #f0fdf4; border-color: #86efac; color: #15803d; }
.ai-btn:hover:not(:disabled) { background: #dcfce7; border-color: #4ade80; }
.ai-spin {
  display: inline-block; width: 13px; height: 13px;
  border: 2px solid #86efac; border-top-color: #15803d;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
.ai-msg { font-size: 12px; padding: 2px 6px; border-radius: 4px; }
.ai-ok   { color: #15803d; background: #dcfce7; }
.ai-warn { color: #b45309; background: #fef3c7; }
.ai-hint-text { font-size: 11px; color: #b45309; font-style: italic; }
.frame-counter { font-size: 13px; color: #6b7280; min-width: 60px; text-align: center; }

.edit-bar { display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; flex-shrink: 0; }
.edit-label { font-size: 13px; font-weight: 600; color: #1d4ed8; }

.no-frame { flex: 1; display: flex; align-items: center; justify-content: center; color: #9ca3af; }

.scrubber { padding: 4px 0; flex-shrink: 0; }
.scrubber-range { width: 100%; accent-color: #4F46E5; }

.thumb-strip { display: flex; gap: 6px; overflow-x: auto; padding: 6px 0; flex-shrink: 0; }
.thumb { position: relative; flex-shrink: 0; width: 72px; cursor: pointer; border: 2px solid transparent; border-radius: 4px; overflow: hidden; }
.thumb.active { border-color: #4F46E5; }
.thumb img { width: 100%; height: 48px; object-fit: cover; display: block; }
.thumb-num { position: absolute; bottom: 2px; left: 3px; font-size: 10px; color: #fff; background: rgba(0,0,0,0.5); padding: 1px 3px; border-radius: 2px; }
.thumb-badge { position: absolute; top: 2px; right: 3px; font-size: 10px; color: #fff; background: #4F46E5; padding: 1px 4px; border-radius: 8px; }
</style>
