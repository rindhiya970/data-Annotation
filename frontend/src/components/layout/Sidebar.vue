<!-- src/components/layout/Sidebar.vue -->
<template>
  <aside class="sb" :class="{ 'sb-open': isOpen }">
    <div class="sb-header">
      <div class="sb-logo">
        <div class="sb-logo-icon">
          <svg width="30" height="30" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="8" fill="#1a1a1a"/>
            <path d="M8 16L14 22L24 10" stroke="#fff59d" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="sb-logo-text">
          <span class="sb-logo-title">DataAnnotate</span>
        </div>
      </div>
    </div>

    <nav class="sb-nav">
      <div class="sb-section">
        <span class="sb-section-label">Main</span>
        <router-link to="/dashboard" class="sb-item" @click="handleNavClick">
          <svg class="sb-icon" width="18" height="18" viewBox="0 0 20 20" fill="none">
            <path d="M3 9L10 2L17 9V17C17 17.53 16.79 18.04 16.41 18.41C16.04 18.79 15.53 19 15 19H5C4.47 19 3.96 18.79 3.59 18.41C3.21 18.04 3 17.53 3 17V9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>Dashboard</span>
        </router-link>
        <router-link to="/projects" class="sb-item" @click="handleNavClick">
          <svg class="sb-icon" width="18" height="18" viewBox="0 0 20 20" fill="none">
            <path d="M2 5C2 3.9 2.9 3 4 3H7L9 6H16C17.1 6 18 6.9 18 8V15C18 16.1 17.1 17 16 17H4C2.9 17 2 16.1 2 15V5Z" stroke="currentColor" stroke-width="2"/>
          </svg>
          <span>Projects</span>
        </router-link>
        <router-link to="/tasks" class="sb-item" @click="handleNavClick">
          <svg class="sb-icon" width="18" height="18" viewBox="0 0 20 20" fill="none">
            <path d="M9 2L2 7L9 12L16 7L9 2Z" stroke="currentColor" stroke-width="2"/>
          </svg>
          <span>Tasks</span>
        </router-link>
        <router-link to="/media/upload" class="sb-item" @click="handleNavClick">
          <svg class="sb-icon" width="18" height="18" viewBox="0 0 20 20" fill="none">
            <path d="M17 13V17C17 18.1 16.1 19 15 19H3C1.9 19 1 18.1 1 17V13" stroke="currentColor" stroke-width="2"/>
            <path d="M14 6L9 1L4 6M9 1V13" stroke="currentColor" stroke-width="2"/>
          </svg>
          <span>Upload</span>
        </router-link>
        <router-link to="/media/library" class="sb-item" @click="handleNavClick">
          <svg class="sb-icon" width="18" height="18" viewBox="0 0 20 20" fill="none">
            <rect x="3" y="3" width="14" height="14" stroke="currentColor" stroke-width="2"/>
            <circle cx="7" cy="10" r="2" stroke="currentColor" stroke-width="2"/>
          </svg>
          <span>Library</span>
        </router-link>
      </div>

      <div class="sb-section">
        <span class="sb-section-label">Account</span>
        <router-link to="/profile" class="sb-item" @click="handleNavClick">
          <svg class="sb-icon" width="18" height="18" viewBox="0 0 20 20" fill="none">
            <circle cx="10" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
            <path d="M2 18C2 15.24 5.58 13 10 13C14.42 13 18 15.24 18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>Profile</span>
        </router-link>
      </div>
    </nav>

    <div class="sb-footer">
      <button class="sb-logout" @click="handleLogout">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M6 14H3.33C2.6 14 2 13.4 2 12.67V3.33C2 2.6 2.6 2 3.33 2H6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          <path d="M10.67 11.33L14 8L10.67 4.67M14 8H6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Logout
      </button>
    </div>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/authStore'

defineProps({ isOpen: Boolean })
const emit = defineEmits(['toggle'])

const router = useRouter()
const authStore = useAuthStore()

const handleNavClick = () => {
  emit('toggle')
}

const handleLogout = () => {
  localStorage.removeItem('da_user_email')
  localStorage.removeItem('da_display_name')
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.sb {
  position: fixed;
  top: 0;
  left: 0;
  width: 260px;
  height: 100vh;
  background: #fffef5;
  border-right: 2px dashed #1a1a1a;
  display: flex;
  flex-direction: column;
  z-index: 1000;
  transform: translateX(-260px);
  transition: transform 0.3s ease;
  overflow-y: auto;
  overflow-x: hidden;
  font-family: 'Patrick Hand', cursive;
}

.sb.sb-open {
  transform: translateX(0);
}

.sb::-webkit-scrollbar { width: 4px; }
.sb::-webkit-scrollbar-track { background: transparent; }
.sb::-webkit-scrollbar-thumb { background: #ccc; border-radius: 2px; }

.sb-header {
  padding: 20px 16px 16px;
  border-bottom: 2px dashed #1a1a1a;
  flex-shrink: 0;
}

.sb-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sb-logo-icon {
  flex-shrink: 0;
  border: 2px solid #1a1a1a;
  border-radius: 8px;
  box-shadow: 2px 2px 0px #1a1a1a;
  padding: 2px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sb-logo-text {
  display: flex;
  flex-direction: column;
  transform: rotate(-1deg);
}

.sb-logo-title {
  font-size: 15px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.2;
  background: linear-gradient(104deg, transparent 0.5%, #fff59d 2%, #fff59d 95%, transparent 99%);
  padding: 1px 5px;
  border-radius: 2px;
  display: inline-block;
}

.sb-nav {
  flex: 1;
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sb-section {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 8px;
}

.sb-section-label {
  font-size: 10px;
  font-weight: 700;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  padding: 8px 8px 4px;
  border-bottom: 1px dashed #ccc;
  margin-bottom: 4px;
}

.sb-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: 7px;
  color: #444;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  font-family: 'Patrick Hand', cursive;
  border: 2px solid transparent;
  background: transparent;
}

.sb-item:hover {
  border: 2px dashed #1a1a1a;
  color: #1a1a1a;
}

.sb-item.router-link-active,
.sb-item.router-link-exact-active {
  background: #fff59d;
  border: 2px solid #1a1a1a;
  box-shadow: 2px 2px 0px #1a1a1a;
  color: #1a1a1a;
  font-weight: 700;
}

.sb-icon {
  flex-shrink: 0;
  opacity: 0.6;
}

.sb-item:hover .sb-icon,
.sb-item.router-link-active .sb-icon,
.sb-item.router-link-exact-active .sb-icon {
  opacity: 1;
}

.sb-footer {
  padding: 14px 16px 20px;
  border-top: 2px dashed #1a1a1a;
  flex-shrink: 0;
}

.sb-logout {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 9px 14px;
  font-family: 'Patrick Hand', cursive;
  font-size: 14px;
  font-weight: 600;
  background: #ffe0e0;
  color: #c0392b;
  border: 2px solid #1a1a1a;
  border-radius: 8px;
  box-shadow: 2px 2px 0px #1a1a1a;
  cursor: pointer;
}

.sb-logout:hover {
  box-shadow: 1px 1px 0px #1a1a1a;
  transform: translate(1px, 1px);
  background: #ffcdd2;
}
</style>