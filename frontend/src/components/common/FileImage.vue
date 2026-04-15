<template>
  <div class="file-image-wrapper">
    <img
      v-if="!error"
      :src="imageUrl"
      :alt="alt"
      :class="imageClass"
      @load="onLoad"
      @error="onError"
      :loading="lazy ? 'lazy' : 'eager'"
    />
    <div v-else class="image-error">
      <span>{{ errorMessage }}</span>
    </div>
    <div v-if="loading" class="image-loading">
      <span>Loading...</span>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { getFileUrl } from '../../config/api'

export default {
  name: 'FileImage',
  props: {
    // Use stored_filename from backend response
    storedFilename: {
      type: String,
      required: true
    },
    alt: {
      type: String,
      default: 'Image'
    },
    imageClass: {
      type: String,
      default: ''
    },
    lazy: {
      type: Boolean,
      default: true
    }
  },
  setup(props) {
    const loading = ref(true)
    const error = ref(false)
    const errorMessage = ref('Failed to load image')

    // Compute the full image URL
    const imageUrl = computed(() => {
      return getFileUrl(props.storedFilename)
    })

    const onLoad = () => {
      loading.value = false
      error.value = false
    }

    const onError = () => {
      loading.value = false
      error.value = true
      console.error(`Failed to load image: ${imageUrl.value}`)
    }

    onMounted(() => {
      if (!props.storedFilename) {
        error.value = true
        errorMessage.value = 'No filename provided'
        loading.value = false
      }
    })

    return {
      loading,
      error,
      errorMessage,
      imageUrl,
      onLoad,
      onError
    }
  }
}
</script>

<style scoped>
.file-image-wrapper {
  position: relative;
  display: inline-block;
}

.image-loading,
.image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
  background-color: #f5f5f5;
  color: #666;
  padding: 1rem;
}

.image-error {
  background-color: #fee;
  color: #c33;
}

img {
  max-width: 100%;
  height: auto;
  display: block;
}
</style>
