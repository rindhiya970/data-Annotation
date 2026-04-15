<!-- src/views/ProfileView.vue -->
<template>
  <div class="pf">

    <h2 class="pf-title">Profile</h2>

    <div class="pf-card">

      <!-- Avatar + name/email -->
      <div class="pf-hero">
        <div class="pf-avatar">{{ initials }}</div>
        <div class="pf-hero-text">
          <div class="pf-name">{{ displayName }}</div>
          <div class="pf-email" v-if="userEmail">{{ userEmail }}</div>
        </div>
      </div>

      <div class="pf-divider"></div>

      <!-- Info rows — view mode -->
      <div v-if="!editing" class="pf-grid">
        <div class="pf-row">
          <span class="pf-label">Name</span>
          <span class="pf-value">{{ displayName }}</span>
        </div>
        <div class="pf-row">
          <span class="pf-label">Email</span>
          <span class="pf-value">{{ userEmail }}</span>
        </div>
        <div class="pf-row" v-if="authStore.user?.created_at">
          <span class="pf-label">Account created</span>
          <span class="pf-value">{{ formatDate(authStore.user.created_at) }}</span>
        </div>
      </div>

      <!-- Edit mode -->
      <div v-else class="pf-grid">
        <div class="pf-row">
          <span class="pf-label">Name</span>
          <input v-model="editName" class="pf-input" placeholder="Enter your name" maxlength="60" />
        </div>
        <div class="pf-row">
          <span class="pf-label">Email</span>
          <span class="pf-value pf-muted">{{ userEmail }} <small>(cannot change)</small></span>
        </div>
      </div>

      <div class="pf-divider"></div>

      <div class="pf-footer">
        <template v-if="!editing">
          <button class="pf-edit-btn" @click="startEdit">✏️ Edit Profile</button>
        </template>
        <template v-else>
          <button class="pf-cancel-btn" @click="cancelEdit">Cancel</button>
          <button class="pf-save-btn" @click="saveEdit">💾 Save</button>
        </template>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/authStore'

const authStore = useAuthStore()

const DISPLAY_NAME_KEY = 'da_display_name'
const EMAIL_KEY = 'da_user_email'

// Email: try authStore first, then localStorage fallback (survives page refresh)
const userEmail = computed(() => {
  const live = authStore.user?.email
  if (live) {
    // Cache it for next refresh
    localStorage.setItem(EMAIL_KEY, live)
    return live
  }
  return localStorage.getItem(EMAIL_KEY) || ''
})

// Display name as a reactive ref — initialised once from localStorage or email prefix
function getInitialName() {
  const saved = localStorage.getItem(DISPLAY_NAME_KEY)
  if (saved) return saved
  const email = authStore.user?.email || localStorage.getItem(EMAIL_KEY) || ''
  return email ? email.split('@')[0] : 'User'
}

const displayName = ref(getInitialName())

const initials = computed(() => {
  const name = displayName.value.trim()
  const parts = name.split(/\s+/)
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return name.substring(0, 2).toUpperCase()
})

// Edit mode
const editing = ref(false)
const editName = ref('')

function startEdit() {
  editName.value = displayName.value
  editing.value = true
}

function cancelEdit() {
  editing.value = false
}

function saveEdit() {
  const trimmed = editName.value.trim()
  if (trimmed) {
    localStorage.setItem(DISPLAY_NAME_KEY, trimmed)
    displayName.value = trimmed   // update the ref → Vue re-renders immediately
  }
  editing.value = false
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<style scoped>
.pf {
  max-width: 600px;
  margin: 0 auto;
  font-family: 'Patrick Hand', cursive;
}

/* ── Page title ── */
.pf-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 28px;
  display: inline-block;
  background: linear-gradient(104deg, transparent 0.5%, #fff59d 2%, #fff59d 95%, transparent 99%);
  padding: 2px 10px;
  border-radius: 3px;
}

/* ── Card ── */
.pf-card {
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 12px;
  box-shadow: 5px 5px 0px #1a1a1a;
  padding: 28px 28px 24px;
}

/* ── Hero row ── */
.pf-hero {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.pf-avatar {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  background: #fff59d;
  border: 2px solid #1a1a1a;
  border-radius: 12px;
  box-shadow: 3px 3px 0px #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  font-weight: 700;
  color: #1a1a1a;
}

.pf-hero-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.pf-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: #1a1a1a;
}

.pf-email {
  font-size: 0.9rem;
  color: #666;
}

/* ── Divider ── */
.pf-divider {
  border: none;
  border-top: 1.5px dashed #ccc;
  margin: 20px 0;
}

/* ── Info grid ── */
.pf-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.pf-row {
  display: grid;
  grid-template-columns: 140px 1fr;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: #fff;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
}

.pf-label {
  font-size: 12px;
  font-weight: 700;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.pf-value {
  font-size: 15px;
  color: #1a1a1a;
  font-weight: 500;
  word-break: break-all;
}

/* ── Footer ── */
.pf-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.pf-edit-btn {
  padding: 9px 20px;
  font-family: 'Patrick Hand', cursive;
  font-size: 14px;
  font-weight: 700;
  background: #fff59d;
  color: #1a1a1a;
  border: 2px solid #1a1a1a;
  border-radius: 8px;
  box-shadow: 3px 3px 0px #1a1a1a;
  cursor: pointer;
}

.pf-edit-btn:hover {
  box-shadow: 1px 1px 0px #1a1a1a;
  transform: translate(1px, 1px);
}

.pf-save-btn {
  padding: 9px 20px;
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

.pf-save-btn:hover {
  box-shadow: 1px 1px 0px #4f46e5;
  transform: translate(1px, 1px);
}

.pf-cancel-btn {
  padding: 9px 20px;
  font-family: 'Patrick Hand', cursive;
  font-size: 14px;
  font-weight: 600;
  background: #fffef5;
  color: #666;
  border: 2px solid #ccc;
  border-radius: 8px;
  box-shadow: 2px 2px 0px #ccc;
  cursor: pointer;
}

.pf-cancel-btn:hover {
  border-color: #1a1a1a;
  color: #1a1a1a;
}

.pf-input {
  flex: 1;
  padding: 7px 10px;
  font-family: 'Patrick Hand', cursive;
  font-size: 15px;
  color: #1a1a1a;
  background: #fff;
  border: 2px solid #4f46e5;
  border-radius: 6px;
  outline: none;
}

.pf-muted small {
  color: #aaa;
  font-size: 12px;
}
</style>