// src/stores/mediaStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fileService } from '../services/fileService'
import { videoService } from '../services/videoService'

export const useMediaStore = defineStore('media', () => {
  // ─── State ────────────────────────────────────────────────────────────────
  const files = ref([])
  const videos = ref([])
  const allMedia = ref([])
  const loading = ref(false)
  const uploading = ref(false)
  const uploadProgress = ref(0)
  const error = ref(null)

  // ─── Actions ──────────────────────────────────────────────────────────────
  
  /**
   * Fetch all media (files + videos) from backend
   */
  async function fetchMedia() {
    loading.value = true
    error.value = null
    
    try {
      console.log('[mediaStore] Fetching all files from /api/files...')
      
      // Only fetch from /api/files since both images and videos are stored there
      const filesResponse = await fileService.getFiles()
      
      console.log('[mediaStore] Files response:', filesResponse)
      
      if (!filesResponse.success) {
        throw new Error(filesResponse.message || 'Failed to fetch files')
      }
      
      const allFiles = filesResponse.data?.files || []
      console.log('[mediaStore] Total files found:', allFiles.length)
      
      // Separate images and videos based on file_type
      files.value = allFiles.filter(file => file.file_type === 'image')
      videos.value = allFiles.filter(file => file.file_type === 'video')
      
      console.log('[mediaStore] Images:', files.value.length, 'Videos:', videos.value.length)

      // Merge and normalize both types
      allMedia.value = allFiles.map(file => ({
        ...file,
        mediaType: file.file_type, // 'image' or 'video'
        id: file.id,
        name: file.original_filename,
        url: file.file_path,
        uploadedAt: file.created_at,
        thumbnail: file.file_path // For images, same as url. For videos, could be different later
      }))

      // Sort by upload date (newest first)
      allMedia.value.sort((a, b) => {
        const dateA = new Date(a.uploadedAt || 0)
        const dateB = new Date(b.uploadedAt || 0)
        return dateB - dateA
      })
      
      console.log('[mediaStore] Final allMedia:', allMedia.value.length, 'items')

      return allMedia.value
    } catch (err) {
      error.value = err.message || 'Failed to fetch media'
      console.error('[mediaStore] Fetch media error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Upload a single file or video
   */
  async function uploadMedia(file, onProgress) {
    uploading.value = true
    uploadProgress.value = 0
    error.value = null

    try {
      // ⚠️ CRITICAL: Pass raw File object, NOT FormData!
      // The service will create FormData internally
      console.log('[mediaStore] Uploading file:', file.name)
      console.log('[mediaStore] File instanceof File:', file instanceof File)
      console.log('[mediaStore] File type:', file.type)
      console.log('[mediaStore] File size:', file.size, 'bytes')

      // Configure upload progress tracking
      const config = {
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          uploadProgress.value = percentCompleted
          if (onProgress) {
            onProgress(percentCompleted)
          }
        }
      }

      // ✅ Pass raw file object directly to fileService
      // fileService.uploadFile() will create FormData internally
      const response = await fileService.uploadFile(file, config)

      console.log('[mediaStore] Upload response:', response)

      // Extract data from standardized response format
      const fileData = response.data || response

      // Add to local state immediately
      const newMedia = {
        ...fileData,
        mediaType: file.type.startsWith('video/') ? 'video' : 'image',
        id: fileData.id || fileData.file_id || fileData.video_id,
        name: fileData.original_filename || file.name,
        url: fileData.file_path || fileData.url,
        uploadedAt: fileData.created_at || new Date().toISOString(),
        thumbnail: fileData.file_path || fileData.url
      }

      allMedia.value.unshift(newMedia)

      if (file.type.startsWith('video/')) {
        videos.value.unshift(fileData)
      } else {
        files.value.unshift(fileData)
      }

      return fileData
    } catch (err) {
      error.value = err.response?.data?.message || `Failed to upload ${file.name}`
      console.error('[mediaStore] Upload error:', err)
      throw err
    } finally {
      uploading.value = false
      uploadProgress.value = 0
    }
  }

  /**
   * Delete media by ID and type
   */
  async function deleteMedia(mediaId, mediaType) {
    try {
      console.log('[mediaStore] Deleting media:', mediaId, mediaType)
      
      // Call the backend delete API
      await fileService.deleteFile(mediaId)
      
      // Remove from local state
      allMedia.value = allMedia.value.filter(m => m.id !== mediaId)
      
      if (mediaType === 'image') {
        files.value = files.value.filter(f => f.id !== mediaId)
      } else {
        videos.value = videos.value.filter(v => v.id !== mediaId)
      }

      console.log('[mediaStore] Media deleted successfully')
      return true
    } catch (err) {
      error.value = err.message || 'Failed to delete media'
      console.error('[mediaStore] Delete failed:', err)
      throw err
    }
  }

  /**
   * Get single media item by ID
   */
  function getMediaById(mediaId) {
    return allMedia.value.find(m => m.id === mediaId)
  }

  /**
   * Clear error state
   */
  function clearError() {
    error.value = null
  }

  return {
    // State
    files,
    videos,
    allMedia,
    loading,
    uploading,
    uploadProgress,
    error,
    
    // Actions
    fetchMedia,
    uploadMedia,
    deleteMedia,
    getMediaById,
    clearError
  }
})