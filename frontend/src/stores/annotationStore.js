// src/stores/annotationStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { annotationService } from '../services/annotationService'

export const useAnnotationStore = defineStore('annotation', () => {
  // State
  const annotations = ref([])
  const selectedAnnotation = ref(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref(null)

  // Actions
  async function fetchAnnotations(fileId) {
    loading.value = true
    error.value = null
    
    try {
      const response = await annotationService.getAnnotationsByFile(fileId)
      
      if (response.success && response.data) {
        annotations.value = response.data
      } else {
        annotations.value = []
      }
      
      return annotations.value
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to load annotations'
      console.error('Failed to fetch annotations:', err)
      annotations.value = []
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createAnnotation(annotationData) {
    saving.value = true
    error.value = null
    
    try {
      const response = await annotationService.createAnnotation(annotationData)
      
      if (response.success && response.data) {
        annotations.value.push(response.data)
        return response.data
      } else {
        throw new Error(response.message || 'Failed to create annotation')
      }
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to create annotation'
      console.error('Failed to create annotation:', err)
      throw err
    } finally {
      saving.value = false
    }
  }

  async function updateAnnotation(annotationId, updates) {
    saving.value = true
    error.value = null
    
    try {
      const response = await annotationService.updateAnnotation(annotationId, updates)
      
      if (response.success && response.data) {
        const index = annotations.value.findIndex(a => a.id === annotationId)
        if (index !== -1) {
          annotations.value[index] = response.data
        }
        return response.data
      } else {
        throw new Error(response.message || 'Failed to update annotation')
      }
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to update annotation'
      console.error('Failed to update annotation:', err)
      throw err
    } finally {
      saving.value = false
    }
  }

  async function deleteAnnotation(annotationId) {
    saving.value = true
    error.value = null
    
    try {
      const response = await annotationService.deleteAnnotation(annotationId)
      
      if (response.success) {
        annotations.value = annotations.value.filter(a => a.id !== annotationId)
        if (selectedAnnotation.value?.id === annotationId) {
          selectedAnnotation.value = null
        }
        return true
      } else {
        throw new Error(response.message || 'Failed to delete annotation')
      }
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to delete annotation'
      console.error('Failed to delete annotation:', err)
      throw err
    } finally {
      saving.value = false
    }
  }

  function selectAnnotation(annotation) {
    selectedAnnotation.value = annotation
  }

  function clearSelection() {
    selectedAnnotation.value = null
  }

  function clearAnnotations() {
    annotations.value = []
    selectedAnnotation.value = null
    error.value = null
  }

  return {
    // State
    annotations,
    selectedAnnotation,
    loading,
    saving,
    error,
    
    // Actions
    fetchAnnotations,
    createAnnotation,
    updateAnnotation,
    deleteAnnotation,
    selectAnnotation,
    clearSelection,
    clearAnnotations
  }
})
