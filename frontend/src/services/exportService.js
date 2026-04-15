// src/services/exportService.js
import API from './api'

export const exportService = {
  /**
   * Export annotations as JSON
   * GET /api/export/json
   */
  async exportJSON() {
    try {
      const response = await API.get('/export/json')
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Export annotations as CSV
   * GET /api/export/csv
   */
  async exportCSV() {
    try {
      const response = await API.get('/export/csv', {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Export annotated image
   * GET /api/export/annotated-image/:fileId
   */
  async exportAnnotatedImage(fileId) {
    try {
      const response = await API.get(`/export/annotated-image/${fileId}`, {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Export annotated video
   * GET /api/export/annotated-video/:videoId
   */
  async exportAnnotatedVideo(videoId) {
    try {
      const response = await API.get(`/export/annotated-video/${videoId}`, {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Export YOLO format for image
   * GET /api/export/yolo/image/:fileId
   */
  async exportYOLOImage(fileId) {
    try {
      const response = await API.get(`/export/yolo/image/${fileId}`, {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Export YOLO format for video
   * GET /api/export/yolo/video/:videoId
   */
  async exportYOLOVideo(videoId) {
    try {
      const response = await API.get(`/export/yolo/video/${videoId}`, {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      throw error
    }
  }
}