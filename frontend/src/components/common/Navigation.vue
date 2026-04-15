<!-- src/components/common/Navigation.vue -->
<template>
  <nav class="navigation">
    <div class="nav-header">
      <div class="logo">
        <span class="logo-icon">📊</span>
        <span class="logo-text">Annotator</span>
      </div>
    </div>
    
    <div class="nav-links">
      <router-link to="/dashboard" class="nav-link">
        <span class="nav-icon">🏠</span>
        <span class="nav-text">Dashboard</span>
      </router-link>
      
      <router-link to="/upload" class="nav-link">
        <span class="nav-icon">📤</span>
        <span class="nav-text">Upload</span>
      </router-link>
      
      <div class="nav-section-title">Media</div>
      
      <router-link to="/files" class="nav-link">
        <span class="nav-icon">🖼️</span>
        <span class="nav-text">Files</span>
      </router-link>
      
      <router-link to="/videos" class="nav-link">
        <span class="nav-icon">🎬</span>
        <span class="nav-text">Videos</span>
      </router-link>
    </div>
  </nav>
</template>

<script setup>
</script>

<style scoped>
.navigation {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 260px;
  background: white;
  border-right: 1px solid #e1e4e8;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  z-index: 200;
}

.nav-header {
  padding: 24px 20px;
  border-bottom: 1px solid #e1e4e8;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #24292e;
}

.nav-links {
  flex: 1;
  padding: 20px 0;
  overflow-y: auto;
}

.nav-section-title {
  padding: 12px 20px 8px;
  font-size: 12px;
  font-weight: 600;
  color: #6a737d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 16px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: #24292e;
  text-decoration: none;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.nav-link:hover {
  background: #f6f8fa;
  color: #0366d6;
}

.nav-link.router-link-active {
  background: #f1f8ff;
  color: #0366d6;
  border-left-color: #0366d6;
  font-weight: 600;
}

.nav-icon {
  font-size: 20px;
  width: 24px;
  text-align: center;
}

.nav-text {
  font-size: 15px;
}

@media (max-width: 768px) {
  .navigation {
    width: 100%;
    height: auto;
    position: relative;
    border-right: none;
    border-bottom: 1px solid #e1e4e8;
  }

  .nav-links {
    display: flex;
    overflow-x: auto;
    padding: 0;
  }

  .nav-section-title {
    display: none;
  }

  .nav-link {
    flex-direction: column;
    padding: 12px 16px;
    gap: 4px;
    border-left: none;
    border-bottom: 3px solid transparent;
    min-width: 80px;
  }

  .nav-link.router-link-active {
    border-left-color: transparent;
    border-bottom-color: #0366d6;
  }

  .nav-text {
    font-size: 12px;
  }
}
</style>