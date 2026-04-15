<!-- src/components/common/ErrorAlert.vue -->
<template>
  <div v-if="message" class="error-alert">
    <span class="error-icon">⚠️</span>
    <span class="error-message">{{ message }}</span>
    <button v-if="dismissible" @click="$emit('dismiss')" class="dismiss-btn">
      ×
    </button>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    required: true
  },
  dismissible: {
    type: Boolean,
    default: true
  }
})

defineEmits(['dismiss'])
</script>

<style scoped>
.error-alert {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff5f5;
  border: 1px solid #fc8181;
  border-radius: 6px;
  color: #c53030;
  margin-bottom: 16px;
}

.error-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.error-message {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

.dismiss-btn {
  background: none;
  border: none;
  color: #c53030;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.dismiss-btn:hover {
  background: rgba(197, 48, 48, 0.1);
}
</style>