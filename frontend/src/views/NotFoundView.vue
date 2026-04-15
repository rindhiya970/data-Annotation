<!-- views/NotFoundView.vue -->
<template>
  <div class="not-found-view">
    <div class="not-found-container">
      <h1>404</h1>
      <p>Page Not Found</p>
      <router-link to="/dashboard">Go to Dashboard</router-link>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.not-found-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}

.not-found-container {
  text-align: center;
}

h1 {
  font-size: 72px;
  margin-bottom: 16px;
  color: #333;
}

p {
  font-size: 24px;
  margin-bottom: 24px;
  color: #666;
}

a {
  display: inline-block;
  padding: 12px 24px;
  background: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 16px;
}

a:hover {
  background: #0056b3;
}
</style>