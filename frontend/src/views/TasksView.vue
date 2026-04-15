<!-- src/views/TasksView.vue -->
<template>
  <div class="tv">

    <!-- Header -->
    <div class="tv-header">
      <div>
        <h2 class="tv-title">Tasks</h2>
        <p class="tv-sub">{{ pending }} pending · {{ done }} completed</p>
      </div>
    </div>

    <!-- Add task form -->
    <form class="tv-form" @submit.prevent="addTask">
      <input
        v-model="newText"
        class="tv-input"
        placeholder="Add a new task and press Enter..."
        maxlength="200"
        autocomplete="off"
      />
      <button type="submit" class="tv-add-btn" :disabled="!newText.trim()">
        + Add
      </button>
    </form>

    <!-- Filter tabs -->
    <div class="tv-tabs">
      <button
        v-for="tab in ['all', 'pending', 'done']"
        :key="tab"
        :class="['tv-tab', { 'tv-tab-active': filter === tab }]"
        @click="filter = tab"
      >
        {{ tab === 'all' ? 'All' : tab === 'pending' ? 'Pending' : 'Completed' }}
        <span class="tv-tab-count">{{ countFor(tab) }}</span>
      </button>
    </div>

    <!-- Empty state -->
    <div v-if="filtered.length === 0" class="tv-empty">
      <span class="tv-empty-icon">{{ filter === 'done' ? '🎉' : '📋' }}</span>
      <p v-if="filter === 'done'">No completed tasks yet.</p>
      <p v-else-if="filter === 'pending'">All caught up!</p>
      <p v-else>No tasks yet. Add one above.</p>
    </div>

    <!-- Task list -->
    <ul v-else class="tv-list">
      <li
        v-for="task in filtered"
        :key="task.id"
        :class="['tv-item', { 'tv-item-done': task.done }]"
      >
        <!-- Checkbox -->
        <button
          class="tv-check"
          :class="{ 'tv-check-done': task.done }"
          @click="toggleTask(task.id)"
          :title="task.done ? 'Mark as pending' : 'Mark as done'"
        >
          <svg v-if="task.done" width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path d="M3 8L6.5 11.5L13 4.5" stroke="currentColor" stroke-width="2.2"
                  stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- Text (editable on double-click) -->
        <span
          v-if="editingId !== task.id"
          class="tv-text"
          @dblclick="startEdit(task)"
          :title="'Double-click to edit'"
        >{{ task.text }}</span>
        <input
          v-else
          v-model="editText"
          class="tv-edit-input"
          @keyup.enter="saveEdit(task.id)"
          @keyup.escape="editingId = null"
          @blur="saveEdit(task.id)"
          ref="editInputRef"
        />

        <!-- Date -->
        <span class="tv-date">{{ formatDate(task.createdAt) }}</span>

        <!-- Delete -->
        <button class="tv-delete" @click="deleteTask(task.id)" title="Delete task">✕</button>
      </li>
    </ul>

    <!-- Clear completed -->
    <div v-if="done > 0" class="tv-footer">
      <button class="tv-clear-btn" @click="clearDone">
        🗑 Clear {{ done }} completed
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useAuthStore } from '../stores/authStore'

const authStore = useAuthStore()

// Per-user storage key — tasks are isolated per account
function storageKey() {
  const uid = authStore.user?.id || 'guest'
  return `da_tasks_v1_${uid}`
}

// ── State ──────────────────────────────────────────────────
function loadTasks() {
  try {
    return JSON.parse(localStorage.getItem(storageKey())) || []
  } catch {
    return []
  }
}

const tasks     = ref(loadTasks())
const newText   = ref('')
const filter    = ref('all')
const editingId = ref(null)
const editText  = ref('')
const editInputRef = ref(null)

// Persist to localStorage whenever tasks change
watch(tasks, (val) => {
  localStorage.setItem(storageKey(), JSON.stringify(val))
}, { deep: true })

// ── Computed ───────────────────────────────────────────────
const pending  = computed(() => tasks.value.filter(t => !t.done).length)
const done     = computed(() => tasks.value.filter(t => t.done).length)

const filtered = computed(() => {
  if (filter.value === 'pending') return tasks.value.filter(t => !t.done)
  if (filter.value === 'done')    return tasks.value.filter(t => t.done)
  return tasks.value
})

function countFor(tab) {
  if (tab === 'all')     return tasks.value.length
  if (tab === 'pending') return pending.value
  return done.value
}

// ── Actions ────────────────────────────────────────────────
function addTask() {
  const text = newText.value.trim()
  if (!text) return
  tasks.value.unshift({
    id:        Date.now(),
    text,
    done:      false,
    createdAt: new Date().toISOString()
  })
  newText.value = ''
}

function toggleTask(id) {
  const t = tasks.value.find(t => t.id === id)
  if (t) t.done = !t.done
}

function deleteTask(id) {
  tasks.value = tasks.value.filter(t => t.id !== id)
}

function clearDone() {
  tasks.value = tasks.value.filter(t => !t.done)
}

function startEdit(task) {
  editingId.value = task.id
  editText.value  = task.text
  nextTick(() => editInputRef.value?.focus())
}

function saveEdit(id) {
  const text = editText.value.trim()
  if (text) {
    const t = tasks.value.find(t => t.id === id)
    if (t) t.text = text
  }
  editingId.value = null
}

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diff = Math.floor((now - d) / 86400000)
  if (diff === 0) return 'Today'
  if (diff === 1) return 'Yesterday'
  if (diff < 7)  return `${diff}d ago`
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.tv {
  max-width: 720px;
  margin: 0 auto;
  font-family: 'Patrick Hand', cursive;
}

/* ── Header ── */
.tv-header {
  margin-bottom: 24px;
}

.tv-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 4px;
  background: linear-gradient(104deg, transparent 0.5%, #fff59d 2%, #fff59d 95%, transparent 99%);
  padding: 2px 8px;
  border-radius: 3px;
  display: inline-block;
}

.tv-sub {
  font-size: 0.88rem;
  color: #666;
  margin: 0;
}

/* ── Add form ── */
.tv-form {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tv-input {
  flex: 1;
  padding: 10px 14px;
  font-family: 'Patrick Hand', cursive;
  font-size: 15px;
  background: #fffef5;
  border: 2px dashed #1a1a1a;
  border-radius: 8px;
  color: #1a1a1a;
  outline: none;
}

.tv-input:focus {
  border-style: solid;
  background: #fff;
}

.tv-add-btn {
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
  white-space: nowrap;
}

.tv-add-btn:hover:not(:disabled) {
  box-shadow: 5px 5px 0px #4f46e5;
  transform: translate(-1px, -1px);
}

.tv-add-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  box-shadow: none;
}

/* ── Filter tabs ── */
.tv-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.tv-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  font-family: 'Patrick Hand', cursive;
  font-size: 13px;
  font-weight: 600;
  background: #fffef5;
  color: #555;
  border: 2px solid #ccc;
  border-radius: 20px;
  cursor: pointer;
}

.tv-tab:hover {
  border-color: #1a1a1a;
  color: #1a1a1a;
}

.tv-tab-active {
  background: #fff59d;
  border-color: #1a1a1a;
  box-shadow: 2px 2px 0px #1a1a1a;
  color: #1a1a1a;
}

.tv-tab-count {
  background: rgba(0,0,0,0.08);
  border-radius: 10px;
  padding: 1px 6px;
  font-size: 11px;
}

/* ── Empty ── */
.tv-empty {
  text-align: center;
  padding: 48px 24px;
  border: 2px dashed #ccc;
  border-radius: 10px;
  background: #fffef5;
  color: #888;
}

.tv-empty-icon { font-size: 2.5rem; display: block; margin-bottom: 12px; }
.tv-empty p { margin: 0; font-size: 0.95rem; }

/* ── Task list ── */
.tv-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tv-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 8px;
  box-shadow: 3px 3px 0px #1a1a1a;
  transition: box-shadow 0.1s, transform 0.1s;
}

.tv-item:hover {
  box-shadow: 4px 4px 0px #1a1a1a;
  transform: translate(-1px, -1px);
}

.tv-item-done {
  background: #f5f5f0;
  border-color: #bbb;
  box-shadow: 2px 2px 0px #bbb;
  opacity: 0.75;
}

.tv-item-done:hover {
  box-shadow: 2px 2px 0px #bbb;
  transform: none;
}

/* Checkbox */
.tv-check {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  background: #fff;
  border: 2px solid #1a1a1a;
  border-radius: 5px;
  box-shadow: 1px 1px 0px #1a1a1a;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.tv-check-done {
  background: #fff59d;
  border-color: #1a1a1a;
  color: #1a1a1a;
}

/* Text */
.tv-text {
  flex: 1;
  font-size: 15px;
  color: #1a1a1a;
  cursor: text;
  word-break: break-word;
}

.tv-item-done .tv-text {
  text-decoration: line-through;
  color: #999;
}

.tv-edit-input {
  flex: 1;
  padding: 4px 8px;
  font-family: 'Patrick Hand', cursive;
  font-size: 15px;
  background: #fff;
  border: 2px solid #4f46e5;
  border-radius: 5px;
  outline: none;
  color: #1a1a1a;
}

/* Date */
.tv-date {
  font-size: 11px;
  color: #aaa;
  white-space: nowrap;
  flex-shrink: 0;
}

/* Delete */
.tv-delete {
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  background: none;
  border: none;
  color: #ccc;
  font-size: 13px;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  box-shadow: none;
}

.tv-delete:hover {
  background: #fce4ec;
  color: #c0392b;
  box-shadow: none;
  transform: none;
}

/* ── Footer ── */
.tv-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.tv-clear-btn {
  padding: 7px 16px;
  font-family: 'Patrick Hand', cursive;
  font-size: 13px;
  font-weight: 600;
  background: #ffe0e0;
  color: #c0392b;
  border: 1.5px solid #1a1a1a;
  border-radius: 7px;
  box-shadow: 2px 2px 0px #1a1a1a;
  cursor: pointer;
}

.tv-clear-btn:hover {
  box-shadow: 1px 1px 0px #1a1a1a;
  transform: translate(1px, 1px);
}
</style>
