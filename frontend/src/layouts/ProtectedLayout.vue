<!-- src/layouts/ProtectedLayout.vue -->
<template>
  <div class="protected-layout">
    <Navigation />
    <div class="main-container">
      <Header />
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import Header from '../components/common/Header.vue'
import Navigation from '../components/common/Navigation.vue'
</script>

<style scoped>
.protected-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f6fa;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 260px;
}

.content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .main-container {
    margin-left: 0;
  }
}
</style>