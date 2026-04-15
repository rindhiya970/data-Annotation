// src/services/fileService.js
import API from './api'

export const fileService = {
  /**
   * Upload a file (image or video)
   * POST /api/files/upload
   * 
   * @param {File} file - The file to upload
   * @param {Object} config - Optional axios config (e.g., onUploadProgress)
   * @returns {Promise} Response with file data
   */
  async uploadFile(file, config = {}) {
    try {
      // Validate file is a File object
      console.log('[fileService] Uploading file:', file.name)
      console.log('[fileService] File instanceof File:', file instanceof File)
      console.log('[fileService] File size:', file.size, 'bytes')
      console.log('[fileService] File type:', file.type)
      
      const formData = new FormData()
      formData.append('file', file)
      
      // Debug: Log FormData contents
      console.log('[fileService] FormData created')
      for (let pair of formData.entries()) {
        console.log('[fileService] FormData entry:', pair[0], pair[1])
      }
      
      // ⚠️ USE NATIVE FETCH INSTEAD OF AXIOS FOR FILE UPLOADS
      // This bypasses any axios configuration issues
      const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api'
      const url = `${baseURL}/files/upload`
      
      console.log('[fileService] Uploading to:', url)
      
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type - let browser handle it
        headers: {
          // Add auth token if present
          ...(localStorage.getItem('token') ? {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          } : {})
        }
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        console.error('[fileService] Upload failed:', data)
        throw new Error(data.message || 'Upload failed')
      }
      
      console.log('[fileService] Upload successful:', data)
      return data
      
    } catch (error) {
      console.error('[fileService] Upload failed - Full error:', error)
      console.error('[fileService] Error message:', error.message)
      throw error
    }
  },

  /**
   * Get all files (optionally filter by type)
   * GET /api/files?type=image or GET /api/files?type=video
   * 
   * @param {string} fileType - Optional filter: 'image' or 'video'
   * @returns {Promise} Response with files array
   */
  async getFiles(fileType = null) {
    try {
      const params = fileType ? { type: fileType } : {}
      const response = await API.get('/files', { params })
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get a specific file
   * GET /api/files/:id
   * 
   * @param {number} fileId - File ID
   * @returns {Promise} Response with file data
   */
  async getFile(fileId) {
    try {
      const response = await API.get(`/files/${fileId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Delete a file
   * DELETE /api/files/:id
   * 
   * @param {number} fileId - File ID
   * @returns {Promise} Response with deletion result
   */
  async deleteFile(fileId) {
    try {
      const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api'
      const url = `${baseURL}/files/${fileId}`
      
      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...(localStorage.getItem('token') ? {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          } : {})
        }
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.message || 'Delete failed')
      }
      
      return data
    } catch (error) {
      console.error('[fileService] Delete failed:', error)
      throw error
    }
  }
}