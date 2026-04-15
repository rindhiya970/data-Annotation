// src/services/annotationService.js
import API from './api'

export const annotationService = {
  /**
   * Create an annotation
   * POST /api/annotations
   */
  async createAnnotation(data) {
    try {
      const response = await API.post('/annotations', data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get annotations by file ID
   * GET /api/annotations/file/:fileId
   */
  async getAnnotationsByFile(fileId) {
    try {
      const response = await API.get(`/annotations/file/${fileId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get annotations by video ID
   * GET /api/annotations/video/:videoId
   */
  async getAnnotationsByVideo(videoId) {
    try {
      const response = await API.get(`/annotations/video/${videoId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Update an annotation
   * PUT /api/annotations/:id
   */
  async updateAnnotation(id, data) {
    try {
      const response = await API.put(`/annotations/${id}`, data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Delete an annotation
   * DELETE /api/annotations/:id
   */
  async deleteAnnotation(id) {
    try {
      const response = await API.delete(`/annotations/${id}`)
      return response.data
    } catch (error) {
      throw error
    }
  }
}