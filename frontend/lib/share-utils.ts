'use client';

import { interactionsAPI } from './api';

export interface ShareData {
  title: string;
  text?: string;
  url: string;
}

export interface ShareOptions {
  onSuccess?: (method: string) => void;
  onError?: (error: Error) => void;
  recordInteraction?: boolean;
  articleId?: string;
  userId?: string;
}

/**
 * Comprehensive share utility that handles multiple fallback methods
 */
export async function shareContent(
  data: ShareData, 
  options: ShareOptions = {}
): Promise<{ success: boolean; method: string }> {
  const { 
    onSuccess, 
    onError, 
    recordInteraction = false, 
    articleId, 
    userId 
  } = options;

  let shareMethod = 'none';
  let shareSuccess = false;

  try {
    // Method 1: Try Web Share API first (mobile browsers)
    if (navigator.share && navigator.canShare) {
      try {
        const shareData = {
          title: data.title,
          text: data.text || data.title,
          url: data.url
        };
        
        if (navigator.canShare(shareData)) {
          await navigator.share(shareData);
          shareMethod = 'native';
          shareSuccess = true;
        }
      } catch (shareError: any) {
        // User cancelled or share failed, try clipboard fallback
        console.log('Native share cancelled or failed:', shareError.message);
        if (shareError.name === 'AbortError') {
          // User cancelled - this is not an error
          return { success: false, method: 'cancelled' };
        }
      }
    }
    
    // Method 2: Modern clipboard API (HTTPS contexts)
    if (!shareSuccess && navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(data.url);
        shareMethod = 'clipboard';
        shareSuccess = true;
        
        // Show visual feedback
        showCopyFeedback();
      } catch (clipboardError) {
        console.log('Clipboard API failed, trying fallback method');
      }
    }
    
    // Method 3: Legacy fallback for older browsers or non-secure contexts
    if (!shareSuccess) {
      try {
        const textArea = document.createElement('textarea');
        textArea.value = data.url;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        textArea.setAttribute('readonly', '');
        document.body.appendChild(textArea);
        
        // Focus and select the text
        textArea.focus();
        textArea.select();
        textArea.setSelectionRange(0, textArea.value.length);
        
        // Execute copy command
        const copySuccess = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (copySuccess) {
          shareMethod = 'fallback';
          shareSuccess = true;
          showCopyFeedback();
        }
      } catch (fallbackError) {
        console.error('All share methods failed:', fallbackError);
      }
    }
    
    // Record the interaction if successful and requested
    if (shareSuccess && recordInteraction && articleId && userId) {
      try {
        await interactionsAPI.share(articleId, shareMethod);
      } catch (apiError) {
        console.error('Failed to record share interaction:', apiError);
        // Don't fail the entire operation for this
      }
    }
    
    // Call success callback
    if (shareSuccess && onSuccess) {
      onSuccess(shareMethod);
    }
    
    return { success: shareSuccess, method: shareMethod };
    
  } catch (error: any) {
    console.error('Share operation failed:', error);
    if (onError) {
      onError(error);
    }
    return { success: false, method: 'error' };
  }
}

/**
 * Show visual feedback when URL is copied to clipboard
 */
function showCopyFeedback() {
  // Create a temporary toast-like notification
  const notification = document.createElement('div');
  notification.textContent = '🔗 Link copied to clipboard!';
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #333;
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    z-index: 10000;
    animation: slideIn 0.3s ease-out;
    pointer-events: none;
  `;
  
  // Add animation styles
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
      from { transform: translateX(0); opacity: 1; }
      to { transform: translateX(100%); opacity: 0; }
    }
  `;
  document.head.appendChild(style);
  document.body.appendChild(notification);
  
  // Remove notification after 3 seconds
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease-in';
    setTimeout(() => {
      if (notification.parentNode) {
        document.body.removeChild(notification);
      }
      if (style.parentNode) {
        document.head.removeChild(style);
      }
    }, 300);
  }, 3000);
}

/**
 * Share an article with proper metadata
 */
export async function shareArticle(
  article: { id: string; title: string; excerpt?: string },
  options: Omit<ShareOptions, 'articleId'> = {}
): Promise<{ success: boolean; method: string }> {
  const shareUrl = `${window.location.origin}/articles/${article.id}`;
  
  return shareContent(
    {
      title: article.title,
      text: article.excerpt || `Check out this article: ${article.title}`,
      url: shareUrl
    },
    {
      ...options,
      articleId: article.id,
      recordInteraction: true
    }
  );
}

/**
 * Generic URL sharing
 */
export async function shareUrl(
  url: string, 
  title: string = 'Check this out!',
  options: ShareOptions = {}
): Promise<{ success: boolean; method: string }> {
  return shareContent(
    {
      title,
      text: title,
      url
    },
    options
  );
}