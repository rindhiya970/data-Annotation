<!-- src/views/AnalyticsView.vue -->
<template>
  <div class="analytics-view">
    <div class="page-header">
      <div>
        <h2 class="page-title">Analytics</h2>
        <p class="page-subtitle">Track your annotation performance</p>
      </div>
    </div>

    <div class="analytics-placeholder">
      <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
        <path d="M110 110H10V10" stroke="#9ca3af" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M110 30L70 50L50 35L10 75" stroke="#4F46E5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="110" cy="30" r="5" fill="#4F46E5"/>
        <circle cx="70" cy="50" r="5" fill="#4F46E5"/>
        <circle cx="50" cy="35" r="5" fill="#4F46E5"/>
        <circle cx="10" cy="75" r="5" fill="#4F46E5"/>
      </svg>
      <h3>Analytics Dashboard</h3>
      <p>Detailed analytics and performance metrics coming soon</p>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.analytics-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 15px;
  color: #6b7280;
  margin: 0;
}

.analytics-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 500px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  text-align: center;
  padding: 40px;
}

.analytics-placeholder h3 {
  font-size: 24px;
  font-weight: 600;
  color: #111827;
  margin: 24px 0 12px 0;
}

.analytics-placeholder p {
  font-size: 15px;
  color: #6b7280;
  margin: 0;
}
</style>