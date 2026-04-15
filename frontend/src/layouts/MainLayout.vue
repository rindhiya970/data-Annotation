<!-- src/layouts/MainLayout.vue -->
<template>
  <div class="ml-root">
    <Sidebar :isOpen="sidebarOpen" @toggle="toggleSidebar" />

    <!-- Overlay: clicking it closes the sidebar -->
    <div v-if="sidebarOpen" class="ml-overlay" @click="toggleSidebar"></div>

    <div class="ml-content">
      <Header @toggleSidebar="toggleSidebar" />
      <main class="ml-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Sidebar from '../components/layout/Sidebar.vue'
import Header from '../components/layout/Header.vue'

// Sidebar is CLOSED by default — opens only when hamburger is clicked
const sidebarOpen = ref(false)

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const handleResize = () => {
  if (window.innerWidth <= 768) {
    sidebarOpen.value = false
  }
}

onMounted(() => window.addEventListener('resize', handleResize))
onUnmounted(() => window.removeEventListener('resize', handleResize))
</script>

<style scoped>
.ml-root {
  display: flex;
  min-height: 100vh;
  background-color: #fdfdf7;
  background-image:
    linear-gradient(rgba(0,0,0,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,0.03) 1px, transparent 1px);
  background-size: 28px 28px;
  font-family: 'Patrick Hand', cursive;
}

/* Content always takes full width — sidebar overlays on top */
.ml-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.ml-main {
  flex: 1;
  padding: 28px 32px;
  overflow-y: auto;
}

/* Dark overlay behind sidebar */
.ml-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 999;
  cursor: pointer;
}

@media (max-width: 768px) {
  .ml-main {
    padding: 16px;
  }
}
</style>