// src/services/videoService.js
import API from './api'

export const videoService = {
  /**
   * NOTE: Videos are uploaded via fileService.uploadFile()
   * There is NO /api/videos/upload endpoint
   * Use: fileService.uploadFile(videoFile) instead
   */

  /**
   * Process a video (extract frames)
   * POST /api/videos/process
   * 
   * @param {number} fileId - ID of the uploaded video file
   * @returns {Promise} Response with video processing results
   */
  async processVideo(fileId) {
    try {
      const response = await API.post('/videos/process', { file_id: fileId })
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get all processed videos
   * GET /api/videos
   * 
   * @returns {Promise} Response with videos array
   */
  async getVideos() {
    try {
      const response = await API.get('/videos')
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get video frames
   * GET /api/videos/:id/frames
   * 
   * @param {number} videoId - Video ID
   * @returns {Promise} Response with frames array
   */
  async getFrames(videoId) {
    try {
      const response = await API.get(`/videos/${videoId}/frames`)
      return response.data
    } catch (error) {
      throw error
    }
  }
}