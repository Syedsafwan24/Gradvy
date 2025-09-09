/**
 * GradvyAnalytics - Comprehensive User Event Tracking System
 * 
 * This analytics library captures user interactions, behavior patterns,
 * and learning activities while respecting privacy settings and GDPR compliance.
 */

class GradvyAnalytics {
  constructor(config = {}) {
    this.config = {
      endpoint: '/api/preferences/interactions/',
      batchSize: 50,
      flushInterval: 10000, // 10 seconds
      maxQueueSize: 1000,
      enableDebug: process.env.NODE_ENV === 'development',
      sessionTimeout: 30 * 60 * 1000, // 30 minutes
      fingerprintingEnabled: true,
      privacyCompliant: true,
      ...config
    };

    // Event queue for batching
    this.eventQueue = [];
    
    // Session management
    this.sessionId = this.generateSessionId();
    this.sessionStartTime = Date.now();
    this.lastActivityTime = Date.now();
    
    // Device and browser info
    this.deviceInfo = this.collectDeviceInfo();
    
    // Privacy settings (fetched from user preferences)
    this.privacySettings = null;
    
    // User context
    this.userContext = {
      userId: null,
      deviceFingerprint: null,
      sessionFingerprint: null,
    };

    this.initialize();
  }

  async initialize() {
    try {
      // Fetch user privacy settings
      await this.fetchPrivacySettings();
      
      // Generate device fingerprint if consent given
      if (this.privacySettings?.behavioralAnalysis && this.config.fingerprintingEnabled) {
        this.userContext.deviceFingerprint = await this.generateDeviceFingerprint();
        this.userContext.sessionFingerprint = this.generateSessionFingerprint();
      }
      
      // Set up automatic flushing
      this.setupAutoFlush();
      
      // Set up page visibility tracking
      this.setupVisibilityTracking();
      
      // Set up automatic page tracking
      this.setupPageTracking();
      
      // Track session start
      this.trackSessionStart();
      
      this.debug('GradvyAnalytics initialized', { 
        sessionId: this.sessionId, 
        privacyEnabled: !!this.privacySettings 
      });
    } catch (error) {
      console.error('Failed to initialize GradvyAnalytics:', error);
    }
  }

  /**
   * Core tracking method - all events go through this
   */
  track(eventType, properties = {}, options = {}) {
    // Check privacy consent before tracking
    if (!this.hasConsentForEvent(eventType)) {
      return this.trackMinimalEvent(eventType);
    }

    const event = {
      // Event identification
      event_id: this.generateEventId(),
      event_type: eventType,
      
      // Timestamps
      timestamp: new Date().toISOString(),
      session_timestamp: Date.now() - this.sessionStartTime,
      
      // User context
      user_id: this.userContext.userId,
      session_id: this.sessionId,
      device_fingerprint: this.userContext.deviceFingerprint,
      session_fingerprint: this.userContext.sessionFingerprint,
      
      // Page context
      page_url: window.location.href,
      page_title: document.title,
      referrer: document.referrer,
      
      // Event data
      properties: this.sanitizeProperties(properties),
      
      // Device and browser context
      device_info: this.deviceInfo,
      
      // Viewport and interaction context
      viewport: this.getViewportInfo(),
      scroll_position: this.getScrollPosition(),
      
      // Options
      immediate_flush: options.immediate || false,
      privacy_level: this.getPrivacyLevel(),
    };

    // Add to queue
    this.eventQueue.push(event);
    
    // Update activity time
    this.updateLastActivity();
    
    // Debug logging
    this.debug('Event tracked:', { eventType, properties, queueSize: this.eventQueue.length });
    
    // Immediate flush if requested or queue is full
    if (options.immediate || this.eventQueue.length >= this.config.batchSize) {
      this.flush();
    }
    
    return event.event_id;
  }

  /**
   * Specialized tracking methods for common interactions
   */
  
  trackPageView(additionalProps = {}) {
    return this.track('page_view', {
      path: window.location.pathname,
      search: window.location.search,
      hash: window.location.hash,
      load_time: performance.now(),
      ...additionalProps
    });
  }

  trackCourseInteraction(courseId, action, properties = {}) {
    return this.track('course_interaction', {
      course_id: courseId,
      action: action, // 'view', 'click', 'enroll', 'start', 'complete', 'bookmark'
      duration: properties.duration || null,
      progress_percentage: properties.progress || null,
      ...properties
    });
  }

  trackLearningActivity(activityType, properties = {}) {
    return this.track('learning_activity', {
      activity_type: activityType, // 'video_watch', 'quiz_attempt', 'reading', 'coding_practice'
      content_id: properties.contentId,
      duration: properties.duration,
      completion_rate: properties.completionRate,
      engagement_score: this.calculateEngagementScore(properties),
      ...properties
    });
  }

  trackQuizAttempt(quizId, properties = {}) {
    return this.track('quiz_attempt', {
      quiz_id: quizId,
      score: properties.score,
      time_taken: properties.timeTaken,
      attempts_count: properties.attempts,
      questions_total: properties.totalQuestions,
      questions_correct: properties.correctAnswers,
      difficulty_level: properties.difficulty,
      ...properties
    });
  }

  trackSearch(query, properties = {}) {
    return this.track('search', {
      query: query,
      results_count: properties.resultsCount,
      filters_applied: properties.filters || [],
      results_clicked: properties.clickedResults || [],
      time_to_first_click: properties.timeToClick,
      ...properties
    });
  }

  trackUserEngagement(engagementType, properties = {}) {
    return this.track('user_engagement', {
      engagement_type: engagementType, // 'focus', 'blur', 'scroll', 'click', 'keyboard'
      element_type: properties.elementType,
      element_id: properties.elementId,
      element_text: properties.elementText?.substring(0, 100), // Limit text length
      mouse_position: properties.mousePosition,
      ...properties
    });
  }

  trackPersonalizationEvent(eventType, properties = {}) {
    return this.track('personalization_event', {
      personalization_type: eventType, // 'recommendation_shown', 'recommendation_clicked', 'preference_updated'
      algorithm_version: properties.algorithmVersion,
      recommendation_id: properties.recommendationId,
      user_feedback: properties.feedback,
      ...properties
    });
  }

  trackErrorEvent(error, properties = {}) {
    return this.track('error_event', {
      error_message: error.message,
      error_stack: error.stack?.substring(0, 500), // Limit stack trace
      error_type: error.constructor.name,
      page_url: window.location.href,
      user_agent: navigator.userAgent,
      ...properties
    }, { immediate: true }); // Flush errors immediately
  }

  /**
   * Session and timing tracking
   */
  
  trackSessionStart() {
    return this.track('session_start', {
      session_id: this.sessionId,
      entry_point: window.location.href,
      referrer: document.referrer,
      is_returning_user: this.isReturningUser(),
      previous_session_time: this.getPreviousSessionTime(),
    });
  }

  trackSessionEnd() {
    const sessionDuration = Date.now() - this.sessionStartTime;
    return this.track('session_end', {
      session_id: this.sessionId,
      session_duration: sessionDuration,
      pages_visited: this.getPagesVisitedCount(),
      interactions_count: this.getInteractionsCount(),
      engagement_score: this.calculateSessionEngagementScore(),
    }, { immediate: true });
  }

  trackTimeOnPage() {
    const timeOnPage = Date.now() - (this.pageStartTime || this.sessionStartTime);
    return this.track('time_on_page', {
      page_url: window.location.href,
      time_spent: timeOnPage,
      scroll_depth: this.getMaxScrollDepth(),
      interactions_count: this.getPageInteractionsCount(),
    });
  }

  /**
   * Advanced behavioral tracking
   */
  
  startActivityTimer(activityId, activityType) {
    this.activeTimers = this.activeTimers || {};
    this.activeTimers[activityId] = {
      startTime: Date.now(),
      activityType: activityType,
      pausedTime: 0,
      interactions: 0
    };
  }

  pauseActivityTimer(activityId) {
    if (this.activeTimers?.[activityId]) {
      this.activeTimers[activityId].pausedAt = Date.now();
    }
  }

  resumeActivityTimer(activityId) {
    if (this.activeTimers?.[activityId]?.pausedAt) {
      const pauseDuration = Date.now() - this.activeTimers[activityId].pausedAt;
      this.activeTimers[activityId].pausedTime += pauseDuration;
      delete this.activeTimers[activityId].pausedAt;
    }
  }

  endActivityTimer(activityId, properties = {}) {
    const timer = this.activeTimers?.[activityId];
    if (!timer) return;

    const totalTime = Date.now() - timer.startTime - timer.pausedTime;
    const activeTime = totalTime - timer.pausedTime;

    this.track('activity_completion', {
      activity_id: activityId,
      activity_type: timer.activityType,
      total_time: totalTime,
      active_time: activeTime,
      paused_time: timer.pausedTime,
      interactions_during_activity: timer.interactions,
      completion_rate: properties.completionRate || 1.0,
      ...properties
    });

    delete this.activeTimers[activityId];
  }

  /**
   * Privacy and consent management
   */
  
  async fetchPrivacySettings() {
    try {
      const response = await fetch('/api/preferences/privacy-settings/');
      if (response.ok) {
        this.privacySettings = await response.json();
      }
    } catch (error) {
      console.warn('Could not fetch privacy settings, using defaults');
      this.privacySettings = { essential: true };
    }
  }

  hasConsentForEvent(eventType) {
    if (!this.config.privacyCompliant || !this.privacySettings) {
      return true; // Default to allowing if privacy not configured
    }

    // Essential events are always allowed
    const essentialEvents = ['session_start', 'session_end', 'error_event'];
    if (essentialEvents.includes(eventType)) {
      return true;
    }

    // Check specific consent requirements
    const consentMapping = {
      'page_view': 'analytics_consent',
      'course_interaction': 'personalization_consent',
      'learning_activity': 'personalization_consent',
      'quiz_attempt': 'personalization_consent',
      'search': 'analytics_consent',
      'user_engagement': 'behavioral_analysis',
      'personalization_event': 'personalization_consent',
    };

    const requiredConsent = consentMapping[eventType] || 'analytics_consent';
    return this.privacySettings[requiredConsent] === true;
  }

  trackMinimalEvent(eventType) {
    // Track minimal event without detailed data for privacy compliance
    const minimalEvent = {
      event_id: this.generateEventId(),
      event_type: eventType,
      timestamp: new Date().toISOString(),
      privacy_limited: true
    };

    this.eventQueue.push(minimalEvent);
    return minimalEvent.event_id;
  }

  getPrivacyLevel() {
    if (!this.privacySettings) return 'unknown';
    
    if (this.privacySettings.behavioral_analysis && 
        this.privacySettings.personalization_consent) {
      return 'full';
    } else if (this.privacySettings.analytics_consent) {
      return 'analytics';
    } else {
      return 'minimal';
    }
  }

  /**
   * Data collection and fingerprinting
   */
  
  collectDeviceInfo() {
    return {
      user_agent: navigator.userAgent,
      screen_resolution: `${screen.width}x${screen.height}`,
      viewport_size: `${window.innerWidth}x${window.innerHeight}`,
      color_depth: screen.colorDepth,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      language: navigator.language,
      languages: navigator.languages,
      platform: navigator.platform,
      cookie_enabled: navigator.cookieEnabled,
      do_not_track: navigator.doNotTrack,
      hardware_concurrency: navigator.hardwareConcurrency,
      memory: navigator.deviceMemory,
      connection_type: navigator.connection?.effectiveType,
      online: navigator.onLine,
    };
  }

  async generateDeviceFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('Device fingerprinting', 2, 2);
    
    const fingerprint = {
      canvas: canvas.toDataURL().slice(22, 32),
      webgl: this.getWebGLFingerprint(),
      audio: await this.getAudioFingerprint(),
      fonts: this.getFontFingerprint(),
      plugins: Array.from(navigator.plugins).map(p => p.name),
    };

    // Create hash from fingerprint data
    const fingerprintString = JSON.stringify(fingerprint);
    return this.hashString(fingerprintString).substring(0, 16);
  }

  generateSessionFingerprint() {
    const sessionData = {
      sessionId: this.sessionId,
      startTime: this.sessionStartTime,
      entryPoint: window.location.href,
      referrer: document.referrer,
      userAgent: navigator.userAgent,
    };

    return this.hashString(JSON.stringify(sessionData)).substring(0, 12);
  }

  /**
   * Utility methods
   */
  
  generateSessionId() {
    return 'sess_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15);
  }

  generateEventId() {
    return 'evt_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
  }

  async hashString(str) {
    const encoder = new TextEncoder();
    const data = encoder.encode(str);
    const hash = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hash))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  sanitizeProperties(properties) {
    const sanitized = {};
    for (const [key, value] of Object.entries(properties)) {
      // Remove sensitive data
      if (typeof value === 'string' && value.length > 1000) {
        sanitized[key] = value.substring(0, 1000) + '...';
      } else if (key.toLowerCase().includes('password') || 
                 key.toLowerCase().includes('secret') ||
                 key.toLowerCase().includes('token')) {
        sanitized[key] = '[REDACTED]';
      } else {
        sanitized[key] = value;
      }
    }
    return sanitized;
  }

  calculateEngagementScore(properties) {
    let score = 0;
    
    // Time-based engagement
    if (properties.duration) {
      score += Math.min(properties.duration / 60000, 1.0) * 0.3; // Max 30% for time
    }
    
    // Completion-based engagement
    if (properties.completionRate) {
      score += properties.completionRate * 0.4; // 40% for completion
    }
    
    // Interaction-based engagement
    if (properties.interactions) {
      score += Math.min(properties.interactions / 10, 1.0) * 0.3; // Max 30% for interactions
    }
    
    return Math.min(score, 1.0);
  }

  /**
   * Data transmission and batching
   */
  
  async flush() {
    if (this.eventQueue.length === 0) return;

    const events = this.eventQueue.splice(0, this.config.batchSize);
    
    try {
      const response = await fetch(this.config.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken(),
        },
        body: JSON.stringify({ events }),
        credentials: 'same-origin'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      this.debug(`Flushed ${events.length} events successfully`);
      
    } catch (error) {
      console.error('Failed to flush analytics events:', error);
      
      // Re-queue events if flush failed (with limit to prevent infinite growth)
      if (this.eventQueue.length < this.config.maxQueueSize - events.length) {
        this.eventQueue.unshift(...events);
      }
    }
  }

  setupAutoFlush() {
    this.flushInterval = setInterval(() => {
      if (this.eventQueue.length > 0) {
        this.flush();
      }
    }, this.config.flushInterval);

    // Flush on page unload
    window.addEventListener('beforeunload', () => {
      this.trackSessionEnd();
      this.flush();
    });

    // Flush on page hide (mobile)
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.flush();
      }
    });
  }

  setupVisibilityTracking() {
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.track('page_blur', {
          time_spent: Date.now() - (this.pageStartTime || this.sessionStartTime)
        });
      } else {
        this.track('page_focus');
        this.pageStartTime = Date.now();
      }
    });
  }

  setupPageTracking() {
    // Track initial page view
    this.pageStartTime = Date.now();
    this.trackPageView();

    // Track route changes (for SPAs)
    const originalPushState = history.pushState;
    const originalReplaceState = history.replaceState;

    history.pushState = (...args) => {
      this.trackTimeOnPage();
      originalPushState.apply(history, args);
      setTimeout(() => this.trackPageView(), 0);
    };

    history.replaceState = (...args) => {
      this.trackTimeOnPage();
      originalReplaceState.apply(history, args);
      setTimeout(() => this.trackPageView(), 0);
    };

    window.addEventListener('popstate', () => {
      this.trackTimeOnPage();
      setTimeout(() => this.trackPageView(), 0);
    });
  }

  /**
   * Helper methods for context information
   */
  
  getViewportInfo() {
    return {
      width: window.innerWidth,
      height: window.innerHeight,
      scroll_x: window.scrollX,
      scroll_y: window.scrollY
    };
  }

  getScrollPosition() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    return {
      pixels: scrollTop,
      percentage: docHeight > 0 ? Math.round((scrollTop / docHeight) * 100) : 0
    };
  }

  getCSRFToken() {
    const cookieMatch = document.cookie.match(/csrftoken=([^;]*)/);
    return cookieMatch ? cookieMatch[1] : '';
  }

  updateLastActivity() {
    this.lastActivityTime = Date.now();
  }

  isReturningUser() {
    return localStorage.getItem('gradvy_returning_user') === 'true' || false;
  }

  debug(message, data = {}) {
    if (this.config.enableDebug) {
      console.log(`[GradvyAnalytics] ${message}`, data);
    }
  }

  /**
   * Public API methods
   */
  
  setUserId(userId) {
    this.userContext.userId = userId;
  }

  updatePrivacySettings(settings) {
    this.privacySettings = { ...this.privacySettings, ...settings };
  }

  // Clean up resources
  destroy() {
    if (this.flushInterval) {
      clearInterval(this.flushInterval);
    }
    
    // Final flush
    this.trackSessionEnd();
    this.flush();
  }
}

// Export singleton instance
export const analytics = new GradvyAnalytics();

// Auto-initialize when module is imported
export default analytics;