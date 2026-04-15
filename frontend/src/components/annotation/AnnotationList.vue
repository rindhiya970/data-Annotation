<!-- src/components/annotation/AnnotationList.vue -->
<template>
  <div class="annotation-list">
    <div class="list-header">
      <h3>Annotations ({{ annotations.length }})</h3>
      <button 
        v-if="annotations.length > 0"
        @click="$emit('clearAll')" 
        class="clear-btn"
        title="Clear all annotations"
      >
        Clear All
      </button>
    </div>

    <div v-if="annotations.length === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
        <rect x="6" y="6" width="36" height="36" rx="2" stroke="#d1d5db" stroke-width="2"/>
        <path d="M6 18L42 18" stroke="#d1d5db" stroke-width="2"/>
        <circle cx="14" cy="12" r="2" fill="#d1d5db"/>
        <circle cx="22" cy="12" r="2" fill="#d1d5db"/>
        <circle cx="30" cy="12" r="2" fill="#d1d5db"/>
      </svg>
      <p>No annotations yet</p>
      <span>Draw a bounding box to start</span>
    </div>

    <div v-else class="list-content">
      <div 
        v-for="(annotation, index) in annotations" 
        :key="annotation.id || index"
        :class="['annotation-item', { selected: selectedAnnotation?.id === annotation.id }]"
        @click="$emit('select', annotation)"
      >
        <div class="annotation-color" :style="{ background: getColor(index) }"></div>
        
        <div class="annotation-info">
          <div class="annotation-label">{{ annotation.label }}</div>
          <div class="annotation-coords">
            x: {{ Math.round(annotation.x) }}, 
            y: {{ Math.round(annotation.y) }}, 
            w: {{ Math.round(annotation.width) }}, 
            h: {{ Math.round(annotation.height) }}
          </div>
        </div>

        <button 
          @click.stop="$emit('delete', annotation)" 
          class="delete-btn"
          title="Delete annotation"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  annotations: {
    type: Array,
    default: () => []
  },
  selectedAnnotation: {
    type: Object,
    default: null
  }
})

defineEmits(['select', 'delete', 'clearAll'])

const colors = [
  '#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6',
  '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#6366f1'
]

function getColor(index) {
  return colors[index % colors.length]
}
</script>

<style scoped>
.annotation-list {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.list-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.clear-btn {
  padding: 6px 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-btn:hover {
  border-color: #ef4444;
  color: #ef4444;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 32px 16px;
  color: #9ca3af;
}

.empty-state svg {
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  margin: 0 0 4px 0;
}

.empty-state span {
  font-size: 12px;
  color: #9ca3af;
}

.list-content {
  flex: 1;
  overflow-y: auto;
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
  flex-shrink: 0;
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
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.annotation-coords {
  font-size: 11px;
  color: #6b7280;
  font-family: 'Courier New', monospace;
}

.delete-btn {
  padding: 4px;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  transition: color 0.2s;
  flex-shrink: 0;
}

.delete-btn:hover {
  color: #ef4444;
}

/* Scrollbar styling */
.list-content::-webkit-scrollbar {
  width: 6px;
}

.list-content::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 3px;
}

.list-content::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.list-content::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
