<!-- src/components/layout/Header.vue -->
<template>
  <header class="hdr">
    <div class="hdr-inner">

      <!-- Hamburger -->
      <button class="hdr-menu-btn" @click="$emit('toggleSidebar')" title="Toggle menu">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <line x1="2" y1="5" x2="18" y2="5" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round"/>
          <line x1="2" y1="10" x2="18" y2="10" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round"/>
          <line x1="2" y1="15" x2="18" y2="15" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round"/>
        </svg>
      </button>

      <!-- Page title + breadcrumb -->
      <div class="hdr-title-block">
        <h1 class="hdr-title">{{ pageTitle }}</h1>
        <p class="hdr-crumb">{{ breadcrumb }}</p>
      </div>

      <!-- Right-side actions -->
      <div class="hdr-actions">

        <!-- Pending tasks notification bell -->
        <button
          class="hdr-icon-btn hdr-notif-btn"
          :title="pendingCount > 0 ? `${pendingCount} pending task${pendingCount > 1 ? 's' : ''}` : 'No pending tasks'"
          @click="$router.push('/tasks')"
        >
          🔔
          <span v-if="pendingCount > 0" class="hdr-badge">{{ pendingCount }}</span>
        </button>

        <!-- User menu -->
        <div class="hdr-user-wrap">
          <button class="hdr-user-btn" @click="toggleUserMenu">
            <div class="hdr-avatar">{{ userInitials }}</div>
            <div class="hdr-user-info">
              <span class="hdr-user-name">{{ userName }}</span>
              <span class="hdr-user-role">Administrator</span>
            </div>
            <svg class="hdr-chevron" width="14" height="14" viewBox="0 0 16 16" fill="none">
              <path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="2"
                    stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>

          <!-- Dropdown -->
          <div v-if="userMenuOpen" class="hdr-dropdown">
            <router-link to="/profile" class="hdr-drop-item" @click="toggleUserMenu">
              <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
                <path d="M13 14V12.6667C13 11.9594 12.719 11.2811 12.219 10.781C11.7189 10.281 11.0406 10 10.3333 10H5.66667C4.95942 10 4.28115 10.281 3.78105 10.781C3.28095 11.2811 3 11.9594 3 12.6667V14"
                      stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M8 7.33333C9.47276 7.33333 10.6667 6.13943 10.6667 4.66667C10.6667 3.19391 9.47276 2 8 2C6.52724 2 5.33333 3.19391 5.33333 4.66667C5.33333 6.13943 6.52724 7.33333 8 7.33333Z"
                      stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>My Profile</span>
            </router-link>
            <button class="hdr-drop-item hdr-drop-logout" @click="handleLogout">
              <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
                <path d="M6 14H3.33333C2.97971 14 2.64057 13.8595 2.39052 13.6095C2.14048 13.3594 2 13.0203 2 12.6667V3.33333C2 2.97971 2.14048 2.64057 2.39052 2.39052C2.64057 2.14048 2.97971 2 3.33333 2H6"
                      stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10.6667 11.3333L14 8L10.6667 4.66667M14 8H6"
                      stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>Logout</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/authStore'

defineEmits(['toggleSidebar'])

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const userMenuOpen = ref(false)

// Reactive pending task count — reads from same localStorage key as TasksView
const taskTick = ref(0)  // increment to force recompute

const pendingCount = computed(() => {
  taskTick.value  // reactive dependency
  try {
    const uid = authStore.user?.id || 'guest'
    const tasks = JSON.parse(localStorage.getItem(`da_tasks_v1_${uid}`)) || []
    return tasks.filter(t => !t.done).length
  } catch {
    return 0
  }
})

function onStorageChange(e) {
  const uid = authStore.user?.id || 'guest'
  if (e.key === `da_tasks_v1_${uid}`) taskTick.value++
}

onMounted(() => window.addEventListener('storage', onStorageChange))
onUnmounted(() => window.removeEventListener('storage', onStorageChange))

const pageTitle = computed(() => {
  const titles = {
    'Dashboard':    'Dashboard',
    'Projects':     'Projects',
    'Tasks':        'Tasks',
    'Analytics':    'Analytics',
    'Profile':      'Profile',
    'MediaUpload':  'Upload Media',
    'MediaLibrary': 'Media Library',
    'Annotate':     'Annotate',
    'VideoDetail':  'Video',
    'VideoAnnotate':'Video Annotate',
  }
  return titles[route.name] || route.name || 'Dashboard'
})

const breadcrumb = computed(() => {
  return `Home / ${pageTitle.value}`
})

const userName = computed(() => {
  return authStore.user?.name || authStore.user?.email || 'User'
})

const userInitials = computed(() => {
  const name = userName.value
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
})

const toggleUserMenu = () => {
  userMenuOpen.value = !userMenuOpen.value
}

const handleLogout = () => {
  localStorage.removeItem('da_user_email')
  localStorage.removeItem('da_display_name')
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* ── Header shell ── */
.hdr {
  background: #fffef5;
  border-bottom: 2px dashed #1a1a1a;
  position: sticky;
  top: 0;
  z-index: 100;
  font-family: 'Patrick Hand', cursive;
}

.hdr-inner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
}

/* ── Hamburger ── */
.hdr-menu-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  background: #fff;
  border: 2px solid #1a1a1a;
  border-radius: 8px;
  box-shadow: 3px 3px 0px #1a1a1a;
  color: #1a1a1a;
  cursor: pointer;
  flex-shrink: 0;
  padding: 0;
}

.hdr-menu-btn:hover {
  box-shadow: 1px 1px 0px #1a1a1a;
  transform: translate(2px, 2px);
}

/* ── Page title ── */
.hdr-title-block {
  flex: 1;
}

.hdr-title {
  font-family: 'Patrick Hand', cursive;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.2;
  display: inline-block;
  transform: rotate(-1deg);
  /* Yellow marker highlight on title */
  background: linear-gradient(
    104deg,
    transparent 0.5%,
    #fff59d 2%,
    #fff59d 95%,
    transparent 99%
  );
  padding: 1px 8px;
  border-radius: 3px;
}

.hdr-crumb {
  font-family: 'Patrick Hand', cursive;
  font-size: 12px;
  color: #777;
  margin: 4px 0 0 4px;
}

/* ── Right actions ── */
.hdr-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* ── Icon buttons (back, notifications) ── */
.hdr-icon-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  background: #fff;
  border: 2px solid #1a1a1a;
  border-radius: 10px;
  box-shadow: 3px 3px 0px #1a1a1a;
  color: #1a1a1a;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
}

.hdr-icon-btn:hover {
  box-shadow: 1px 1px 0px #1a1a1a;
  transform: translate(2px, 2px);
}

/* Notification badge */
.hdr-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 18px;
  height: 18px;
  background: #1a1a1a;
  color: #fffef5;
  border-radius: 50%;
  font-size: 10px;
  font-weight: 700;
  font-family: 'Patrick Hand', cursive;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #fffef5;
}

/* ── User button ── */
.hdr-user-wrap {
  position: relative;
}

.hdr-user-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px 6px 6px;
  background: #fff;
  border: 2px solid #1a1a1a;
  border-radius: 10px;
  box-shadow: 3px 3px 0px #1a1a1a;
  cursor: pointer;
  font-family: 'Patrick Hand', cursive;
}

.hdr-user-btn:hover {
  box-shadow: 1px 1px 0px #1a1a1a;
  transform: translate(2px, 2px);
}

.hdr-avatar {
  width: 34px;
  height: 34px;
  background: #fff59d;
  border: 2px solid #1a1a1a;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: #1a1a1a;
  font-family: 'Patrick Hand', cursive;
  flex-shrink: 0;
}

.hdr-user-info {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.hdr-user-name {
  font-size: 13px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.2;
  font-family: 'Patrick Hand', cursive;
}

.hdr-user-role {
  font-size: 11px;
  color: #666;
  font-family: 'Patrick Hand', cursive;
}

.hdr-chevron {
  color: #1a1a1a;
  flex-shrink: 0;
}

/* ── Dropdown ── */
.hdr-dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 190px;
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 10px;
  box-shadow: 4px 4px 0px #1a1a1a;
  overflow: hidden;
  z-index: 200;
}

.hdr-drop-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 11px 14px;
  background: none;
  border: none;
  border-bottom: 1px dashed #ccc;
  color: #1a1a1a;
  font-size: 14px;
  font-family: 'Patrick Hand', cursive;
  text-decoration: none;
  cursor: pointer;
  text-align: left;
}

.hdr-drop-item:last-child {
  border-bottom: none;
}

.hdr-drop-item:hover {
  background: #fff59d;
}

.hdr-drop-logout {
  color: #c0392b;
}

.hdr-drop-logout:hover {
  background: #fce4ec;
}

/* ── Responsive ── */
@media (max-width: 1024px) {
  .hdr-user-info {
    display: none;
  }
  .hdr-user-btn {
    padding: 6px;
  }
}

@media (max-width: 640px) {
  .hdr-inner {
    padding: 10px 14px;
  }
  .hdr-crumb {
    display: none;
  }
  /* hide back button on small screens */
  .hdr-icon-btn:first-child {
    display: none;
  }
}
</style>
