import React, { useState } from 'react';
import { getFileUrl, getFileUrlFromFilename } from '../../config/api';

/**
 * FileImage Component
 * Displays images from Flask backend with proper error handling
 */
const FileImage = ({ 
  file, 
  alt, 
  className = '', 
  style = {},
  onLoad,
  onError 
}) => {
  const [imageError, setImageError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Construct image URL from file object
  const getImageUrl = () => {
    if (!file) return '';
    
    // Try file_path first (full path from backend)
    if (file.file_path) {
      return getFileUrl(file.file_path);
    }
    
    // Fallback to stored_filename
    if (file.stored_filename) {
      return getFileUrlFromFilename(file.stored_filename);
    }
    
    return '';
  };

  const imageUrl = getImageUrl();
  const altText = alt || file?.original_filename || 'Uploaded image';

  const handleImageLoad = (e) => {
    setIsLoading(false);
    if (onLoad) onLoad(e);
  };

  const handleImageError = (e) => {
    setIsLoading(false);
    setImageError(true);
    console.error('Failed to load image:', imageUrl);
    if (onError) onError(e);
  };

  // Show error state
  if (imageError) {
    return (
      <div 
        className={`file-image-error ${className}`} 
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '200px',
          background: '#fee',
          border: '2px dashed #c33',
          borderRadius: '8px',
          color: '#c33',
          padding: '20px',
          ...style
        }}
      >
        <div style={{ fontSize: '48px', marginBottom: '12px' }}>📷</div>
        <p style={{ fontWeight: 600, margin: '0 0 8px 0' }}>Failed to load image</p>
        <p style={{ fontSize: '14px', color: '#666', margin: 0 }}>
          {file?.original_filename}
        </p>
      </div>
    );
  }

  // Show loading state
  if (isLoading) {
    return (
      <div 
        className={`file-image-loading ${className}`} 
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '200px',
          background: '#f5f5f5',
          borderRadius: '8px',
          color: '#666',
          ...style
        }}
      >
        <div 
          style={{
            width: '40px',
            height: '40px',
            border: '4px solid #f3f3f3',
            borderTop: '4px solid #007bff',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            marginBottom: '12px'
          }}
        />
        <p>Loading image...</p>
      </div>
    );
  }

  return (
    <img
      src={imageUrl}
      alt={altText}
      className={`file-image ${className}`}
      style={{
        maxWidth: '100%',
        height: 'auto',
        display: 'block',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        ...style
      }}
      onLoad={handleImageLoad}
      onError={handleImageError}
      loading="lazy"
    />
  );
};

export default FileImage;
