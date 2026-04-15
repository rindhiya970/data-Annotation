<template>
  <div class="canvas-outer">
    <!-- Zoom / Pan toolbar -->
    <div class="zoom-bar">
      <button @click="zoomIn" title="Zoom In">＋</button>
      <button @click="zoomOut" title="Zoom Out">－</button>
      <button @click="resetView" title="Reset View">⊡ Reset</button>
      <span class="zoom-label">{{ Math.round(scale * 100) }}%</span>
      <span class="divider">|</span>
      <button @click="undo" :disabled="undoStack.length === 0" title="Undo (Ctrl+Z)">↩ Undo</button>
      <button @click="redo" :disabled="redoStack.length === 0" title="Redo (Ctrl+Y)">↪ Redo</button>
    </div>

    <!-- Canvas container (scrollable / pannable) -->
    <div
      class="canvas-wrapper"
      ref="wrapperRef"
      @wheel.prevent="handleWheel"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseUp"
      :style="{ cursor: activeCursor }"
    >
      <canvas ref="canvasRef"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  imageUrl:           { type: String,  required: true },
  annotations:        { type: Array,   default: () => [] },
  selectedAnnotation: { type: Object,  default: null },
  mode:               { type: String,  default: 'draw' },
  currentLabel:       { type: String,  default: 'object' }
})

const emit = defineEmits([
  'annotationCreated', 'annotationSelected',
  'annotationMoved',   'annotationResized'
])

// ── Refs ───────────────────────────────────────────────────
const canvasRef  = ref(null)
const wrapperRef = ref(null)
const image      = ref(null)
const imageLoaded = ref(false)

// Viewport transform
const scale     = ref(1)
const panX      = ref(0)
const panY      = ref(0)
const MIN_SCALE = 0.2
const MAX_SCALE = 8

// Draw mode
const isDrawing = ref(false)
const drawStart = ref({ x: 0, y: 0 })
const currentBox = ref(null)

// Select / move / resize
const HANDLE = 8
const dragState = ref(null)

// Pan mode (middle-mouse or space+drag)
const isPanning   = ref(false)
const panStart    = ref({ x: 0, y: 0 })
const spaceDown   = ref(false)

// Undo / Redo stacks  (each entry = snapshot of annotations array)
const undoStack = ref([])
const redoStack = ref([])

// ── Colors ─────────────────────────────────────────────────
const COLORS = [
  '#ef4444','#f59e0b','#10b981','#3b82f6','#8b5cf6',
  '#ec4899','#14b8a6','#f97316','#06b6d4','#6366f1'
]
function getColor(i) { return COLORS[i % COLORS.length] }

// ── Cursor ─────────────────────────────────────────────────
const activeCursor = computed(() => {
  if (isPanning.value || spaceDown.value) return isPanning.value ? 'grabbing' : 'grab'
  if (props.mode === 'draw') return 'crosshair'
  if (dragState.value) return dragState.value.type === 'move' ? 'grabbing' : 'nwse-resize'
  return 'default'
})

// ── Image loading ──────────────────────────────────────────
function loadImage() {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      image.value = img
      imageLoaded.value = true
      fitToView()
      resolve()
    }
    img.onerror = () => reject(new Error('Failed to load image'))
    img.src = props.imageUrl
  })
}

function fitToView() {
  const canvas  = canvasRef.value
  const wrapper = wrapperRef.value
  if (!canvas || !image.value || !wrapper) return
  const ww = wrapper.clientWidth  || 800
  const wh = wrapper.clientHeight || 600
  canvas.width  = ww
  canvas.height = wh
  const s = Math.min(ww / image.value.width, wh / image.value.height, 1)
  scale.value = s
  panX.value  = (ww - image.value.width  * s) / 2
  panY.value  = (wh - image.value.height * s) / 2
  draw()
}

function resetView() { fitToView() }
function zoomIn()    { applyZoom(scale.value * 1.25) }
function zoomOut()   { applyZoom(scale.value / 1.25) }

function applyZoom(newScale, cx, cy) {
  const canvas = canvasRef.value
  if (!canvas) return
  newScale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, newScale))
  const ox = cx ?? canvas.width  / 2
  const oy = cy ?? canvas.height / 2
  panX.value = ox - (ox - panX.value) * (newScale / scale.value)
  panY.value = oy - (oy - panY.value) * (newScale / scale.value)
  scale.value = newScale
  draw()
}

// ── Coordinate helpers ─────────────────────────────────────
// canvas px → image px
function toImage(cx, cy) {
  return { x: (cx - panX.value) / scale.value, y: (cy - panY.value) / scale.value }
}
// image px → canvas px
function toCanvas(ix, iy) {
  return { x: ix * scale.value + panX.value, y: iy * scale.value + panY.value }
}

function getMousePos(e) {
  const rect = canvasRef.value.getBoundingClientRect()
  return { x: e.clientX - rect.left, y: e.clientY - rect.top }
}

// ── Draw ───────────────────────────────────────────────────
function draw() {
  const canvas = canvasRef.value
  if (!canvas || !image.value) return
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // Image
  ctx.save()
  ctx.translate(panX.value, panY.value)
  ctx.scale(scale.value, scale.value)
  ctx.drawImage(image.value, 0, 0)
  ctx.restore()

  // Annotations
  props.annotations.forEach((ann, idx) => {
    const color = getColor(idx)
    const sel   = props.selectedAnnotation?.id === ann.id
    const { x: cx, y: cy } = toCanvas(ann.x, ann.y)
    const cw = ann.width  * scale.value
    const ch = ann.height * scale.value

    ctx.strokeStyle = color
    ctx.lineWidth   = sel ? 3 : 2
    if (ann.ai) ctx.setLineDash([6, 3])
    ctx.strokeRect(cx, cy, cw, ch)
    ctx.setLineDash([])

    // Label badge
    ctx.font = `bold ${Math.max(11, 13 * scale.value)}px Arial`
    const tw = ctx.measureText(ann.label).width
    ctx.fillStyle = color
    ctx.fillRect(cx, cy - 22 * Math.max(0.8, scale.value), tw + 12, 22 * Math.max(0.8, scale.value))
    ctx.fillStyle = '#fff'
    ctx.fillText(ann.label, cx + 6, cy - 6 * Math.max(0.8, scale.value))

    // Handles
    if (sel) {
      getHandles(ann).forEach(h => {
        const hc = toCanvas(h.x, h.y)
        ctx.fillStyle   = '#fff'
        ctx.strokeStyle = color
        ctx.lineWidth   = 2
        ctx.fillRect  (hc.x - HANDLE / 2, hc.y - HANDLE / 2, HANDLE, HANDLE)
        ctx.strokeRect(hc.x - HANDLE / 2, hc.y - HANDLE / 2, HANDLE, HANDLE)
      })
    }
  })

  // Live draw box
  if (isDrawing.value && currentBox.value) {
    const b  = currentBox.value
    const p1 = toCanvas(b.x, b.y)
    ctx.strokeStyle = '#4F46E5'
    ctx.lineWidth   = 2
    ctx.setLineDash([5, 5])
    ctx.strokeRect(p1.x, p1.y, b.width * scale.value, b.height * scale.value)
    ctx.setLineDash([])
  }
}

// ── Handles ────────────────────────────────────────────────
function getHandles(ann) {
  const { x, y, width: w, height: h } = ann
  return [
    { x, y },             { x: x+w/2, y },       { x: x+w, y },
    { x: x+w, y: y+h/2 },{ x: x+w, y: y+h },    { x: x+w/2, y: y+h },
    { x, y: y+h },        { x, y: y+h/2 }
  ]
}

function hitHandle(ann, canvasPos) {
  return getHandles(ann).findIndex(h => {
    const hc = toCanvas(h.x, h.y)
    return Math.abs(canvasPos.x - hc.x) <= HANDLE && Math.abs(canvasPos.y - hc.y) <= HANDLE
  })
}

function hitBox(ann, imgPos) {
  return imgPos.x >= ann.x && imgPos.x <= ann.x + ann.width &&
         imgPos.y >= ann.y && imgPos.y <= ann.y + ann.height
}

// ── Undo / Redo ────────────────────────────────────────────
function snapshot() {
  undoStack.value.push(JSON.stringify(props.annotations))
  redoStack.value = []
}

function undo() {
  if (!undoStack.value.length) return
  redoStack.value.push(JSON.stringify(props.annotations))
  const prev = JSON.parse(undoStack.value.pop())
  // Restore by mutating each annotation in place
  props.annotations.splice(0, props.annotations.length, ...prev)
  draw()
}

function redo() {
  if (!redoStack.value.length) return
  undoStack.value.push(JSON.stringify(props.annotations))
  const next = JSON.parse(redoStack.value.pop())
  props.annotations.splice(0, props.annotations.length, ...next)
  draw()
}

// ── Mouse events ───────────────────────────────────────────
function handleWheel(e) {
  const pos = getMousePos(e)
  applyZoom(scale.value * (e.deltaY < 0 ? 1.1 : 0.9), pos.x, pos.y)
}

function handleMouseDown(e) {
  const cpos = getMousePos(e)
  const ipos = toImage(cpos.x, cpos.y)

  // Middle mouse or space+left = pan
  if (e.button === 1 || (e.button === 0 && spaceDown.value)) {
    isPanning.value = true
    panStart.value  = { x: e.clientX - panX.value, y: e.clientY - panY.value }
    return
  }

  if (props.mode === 'draw') {
    if (!props.currentLabel.trim()) { alert('Enter a label first'); return }
    isDrawing.value  = true
    drawStart.value  = ipos
    currentBox.value = { x: ipos.x, y: ipos.y, width: 0, height: 0 }
    return
  }

  // Select mode
  if (props.selectedAnnotation) {
    const hi = hitHandle(props.selectedAnnotation, cpos)
    if (hi !== -1) {
      snapshot()
      const sel = props.selectedAnnotation
      dragState.value = { type: 'resize', handleIndex: hi, startX: ipos.x, startY: ipos.y,
        origBox: { x: sel.x, y: sel.y, width: sel.width, height: sel.height } }
      return
    }
    if (hitBox(props.selectedAnnotation, ipos)) {
      snapshot()
      const sel = props.selectedAnnotation
      dragState.value = { type: 'move', startX: ipos.x, startY: ipos.y,
        origBox: { x: sel.x, y: sel.y, width: sel.width, height: sel.height } }
      return
    }
  }

  const clicked = [...props.annotations].reverse().find(a => hitBox(a, ipos))
  emit('annotationSelected', clicked || null)
  draw()
}

function handleMouseMove(e) {
  if (isPanning.value) {
    panX.value = e.clientX - panStart.value.x
    panY.value = e.clientY - panStart.value.y
    draw(); return
  }

  const cpos = getMousePos(e)
  const ipos = toImage(cpos.x, cpos.y)

  if (props.mode === 'draw' && isDrawing.value) {
    currentBox.value = {
      x: Math.min(drawStart.value.x, ipos.x),
      y: Math.min(drawStart.value.y, ipos.y),
      width:  Math.abs(ipos.x - drawStart.value.x),
      height: Math.abs(ipos.y - drawStart.value.y)
    }
    draw(); return
  }

  if (!dragState.value || !props.selectedAnnotation) return
  const dx = ipos.x - dragState.value.startX
  const dy = ipos.y - dragState.value.startY
  const ob = dragState.value.origBox
  const sel = props.selectedAnnotation

  if (dragState.value.type === 'move') {
    sel.x = ob.x + dx; sel.y = ob.y + dy
  } else {
    const hi = dragState.value.handleIndex
    let { x, y, width, height } = ob
    if (hi===0){x=ob.x+dx;y=ob.y+dy;width=ob.width-dx;height=ob.height-dy}
    else if(hi===1){y=ob.y+dy;height=ob.height-dy}
    else if(hi===2){y=ob.y+dy;width=ob.width+dx;height=ob.height-dy}
    else if(hi===3){width=ob.width+dx}
    else if(hi===4){width=ob.width+dx;height=ob.height+dy}
    else if(hi===5){height=ob.height+dy}
    else if(hi===6){x=ob.x+dx;width=ob.width-dx;height=ob.height+dy}
    else if(hi===7){x=ob.x+dx;width=ob.width-dx}
    if(width>5){sel.x=x;sel.width=width}
    if(height>5){sel.y=y;sel.height=height}
  }
  draw()
}

function handleMouseUp(e) {
  if (isPanning.value) { isPanning.value = false; return }

  if (props.mode === 'draw' && isDrawing.value) {
    isDrawing.value = false
    if (currentBox.value?.width > 5 && currentBox.value?.height > 5) {
      emit('annotationCreated', {
        label:  props.currentLabel.trim(),
        x:      Math.round(currentBox.value.x),
        y:      Math.round(currentBox.value.y),
        width:  Math.round(currentBox.value.width),
        height: Math.round(currentBox.value.height)
      })
    }
    currentBox.value = null; draw(); return
  }

  if (dragState.value && props.selectedAnnotation) {
    const sel  = props.selectedAnnotation
    const type = dragState.value.type
    dragState.value = null
    if (type === 'move')
      emit('annotationMoved',   { id: sel.id, x: Math.round(sel.x), y: Math.round(sel.y) })
    else
      emit('annotationResized', { id: sel.id, x: Math.round(sel.x), y: Math.round(sel.y), width: Math.round(sel.width), height: Math.round(sel.height) })
    draw()
  }
}

// ── Keyboard shortcuts ─────────────────────────────────────
function onKeyDown(e) {
  if (e.code === 'Space') { spaceDown.value = true; e.preventDefault() }
  if ((e.ctrlKey || e.metaKey) && e.key === 'z') { undo(); e.preventDefault() }
  if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.shiftKey && e.key === 'z'))) { redo(); e.preventDefault() }
  if (e.key === 'Delete' && props.selectedAnnotation) emit('annotationSelected', { ...props.selectedAnnotation, _delete: true })
}
function onKeyUp(e) { if (e.code === 'Space') spaceDown.value = false }

// ── Watchers & lifecycle ───────────────────────────────────
watch(() => props.annotations, () => draw(), { deep: true })
watch(() => props.selectedAnnotation, () => draw())
watch(() => props.imageUrl, () => { imageLoaded.value = false; loadImage() })

function onResize() { if (imageLoaded.value) fitToView() }

onMounted(() => {
  loadImage()
  window.addEventListener('resize', onResize)
  window.addEventListener('keydown', onKeyDown)
  window.addEventListener('keyup',   onKeyUp)
})
onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  window.removeEventListener('keydown', onKeyDown)
  window.removeEventListener('keyup',   onKeyUp)
})

// Expose for parent
defineExpose({ undo, redo, zoomIn, zoomOut, resetView })
</script>

<style scoped>
.canvas-outer {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  background: #f3f4f6;
}

.zoom-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.zoom-bar button {
  padding: 4px 10px;
  border: 1px solid #d1d5db;
  border-radius: 5px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  color: #374151;
  transition: all 0.15s;
}

.zoom-bar button:hover:not(:disabled) {
  background: #4F46E5;
  color: #fff;
  border-color: #4F46E5;
}

.zoom-bar button:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.zoom-label {
  font-size: 13px;
  color: #6b7280;
  min-width: 44px;
  text-align: center;
}

.divider {
  color: #d1d5db;
  margin: 0 4px;
}

.canvas-wrapper {
  flex: 1;
  overflow: hidden;
  position: relative;
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
