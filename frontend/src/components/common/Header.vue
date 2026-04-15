<!-- src/components/common/Header.vue -->
<template>
  <header class="header">
    <div class="header-content">
      <h1 class="app-title">Data Annotation System</h1>
      <div class="user-section">
        <span class="user-email">{{ userEmail }}</span>
        <button @click="handleLogout" class="logout-btn">
          Logout
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const userEmail = computed(() => {
  return authStore.user?.email || 'User'
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.header {
  background: white;
  border-bottom: 1px solid #e1e4e8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  max-width: 100%;
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  color: #24292e;
  margin: 0;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-email {
  font-size: 14px;
  color: #586069;
  font-weight: 500;
}

.logout-btn {
  padding: 8px 16px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.logout-btn:hover {
  background: #c82333;
}

@media (max-width: 768px) {
  .header-content {
    padding: 12px 16px;
  }

  .app-title {
    font-size: 16px;
  }

  .user-email {
    display: none;
  }
}
</style>