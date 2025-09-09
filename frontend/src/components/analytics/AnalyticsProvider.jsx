/**
 * Analytics Provider Component
 * Provides analytics context and automatic tracking capabilities to the entire app
 */

'use client';

import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import analytics from '@/services/analytics';
import useAnalytics from '@/hooks/useAnalytics';

const AnalyticsContext = createContext(null);

export function AnalyticsProvider({ 
  children, 
  userId = null, 
  enableAutoTracking = true,
  privacySettings = null 
}) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [isInitialized, setIsInitialized] = useState(false);
  const [privacyConsent, setPrivacyConsent] = useState(privacySettings);
  
  const {
    track,
    trackCourseView,
    trackCourseEnrollment,
    trackLearningProgress,
    trackQuiz,
    trackSearch,
    trackRecommendation,
    startActivity,
    pauseActivity,
    resumeActivity,
    endActivity,
    trackPerformance,
    trackError,
    setUserId: setAnalyticsUserId,
    updatePrivacySettings
  } = useAnalytics();

  // Initialize analytics when component mounts
  useEffect(() => {
    const initializeAnalytics = async () => {
      try {
        // Set user ID if provided
        if (userId) {
          setAnalyticsUserId(userId);
        }

        // Update privacy settings
        if (privacySettings) {
          updatePrivacySettings(privacySettings);
          setPrivacyConsent(privacySettings);
        }

        // Track app initialization
        track('app_initialized', {
          user_id: userId,
          initial_path: pathname,
          initial_search: searchParams?.toString(),
          privacy_level: getPrivacyLevel(privacySettings),
        });

        setIsInitialized(true);
      } catch (error) {
        console.error('Failed to initialize analytics:', error);
        trackError(error, { context: 'analytics_initialization' });
      }
    };

    initializeAnalytics();
  }, [userId, privacySettings, pathname, searchParams, track, trackError, setAnalyticsUserId, updatePrivacySettings]);

  // Track route changes
  useEffect(() => {
    if (isInitialized && enableAutoTracking) {
      track('route_change', {
        path: pathname,
        search: searchParams?.toString(),
        referrer: document.referrer,
      });
    }
  }, [pathname, searchParams, isInitialized, enableAutoTracking, track]);

  // Track performance metrics
  useEffect(() => {
    if (isInitialized && enableAutoTracking) {
      // Track page load performance
      if (typeof window !== 'undefined' && window.performance) {
        const navigationTiming = performance.getEntriesByType('navigation')[0];
        if (navigationTiming) {
          trackPerformance('page_load', navigationTiming.loadEventEnd - navigationTiming.loadEventStart, {
            dns_lookup: navigationTiming.domainLookupEnd - navigationTiming.domainLookupStart,
            tcp_connection: navigationTiming.connectEnd - navigationTiming.connectStart,
            server_response: navigationTiming.responseEnd - navigationTiming.requestStart,
            dom_processing: navigationTiming.domContentLoadedEventEnd - navigationTiming.domContentLoadedEventStart,
          });
        }

        // Track Core Web Vitals
        trackCoreWebVitals();
      }
    }
  }, [isInitialized, enableAutoTracking, trackPerformance]);

  // Privacy consent management
  const requestPrivacyConsent = useCallback(async (consentTypes) => {
    try {
      // Make API call to record consent
      const response = await fetch('/api/preferences/consent/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          consent_types: consentTypes,
          user_agent: navigator.userAgent,
          timestamp: new Date().toISOString(),
        }),
      });

      if (response.ok) {
        const updatedSettings = await response.json();
        setPrivacyConsent(updatedSettings);
        updatePrivacySettings(updatedSettings);

        track('privacy_consent_updated', {
          consent_types: consentTypes,
          consent_level: getPrivacyLevel(updatedSettings),
        });

        return updatedSettings;
      }
    } catch (error) {
      console.error('Failed to update privacy consent:', error);
      trackError(error, { context: 'privacy_consent_update' });
    }
    
    return null;
  }, [track, trackError, updatePrivacySettings]);

  // Specialized tracking methods with context
  const trackCourseInteraction = useCallback((courseId, action, courseData = {}) => {
    return track('course_interaction', {
      course_id: courseId,
      action: action,
      course_title: courseData.title,
      course_category: courseData.category,
      course_difficulty: courseData.difficulty,
      course_provider: courseData.provider,
      user_enrollment_status: courseData.enrollmentStatus,
      recommendation_source: courseData.recommendationSource,
    });
  }, [track]);

  const trackLearningSession = useCallback((sessionData) => {
    return track('learning_session', {
      session_type: sessionData.type, // 'video', 'reading', 'practice', 'quiz'
      content_id: sessionData.contentId,
      session_duration: sessionData.duration,
      completion_rate: sessionData.completionRate,
      engagement_score: sessionData.engagementScore,
      interactions_count: sessionData.interactionsCount,
      difficulty_rating: sessionData.difficultyRating,
      user_rating: sessionData.userRating,
    });
  }, [track]);

  const trackPersonalizationFeedback = useCallback((feedbackData) => {
    return trackRecommendation('user_feedback', {
      recommendation_id: feedbackData.recommendationId,
      feedback_type: feedbackData.type, // 'thumbs_up', 'thumbs_down', 'not_relevant', 'helpful'
      feedback_reason: feedbackData.reason,
      recommendation_accuracy: feedbackData.accuracy,
      user_segment: feedbackData.userSegment,
    });
  }, [trackRecommendation]);

  const trackGoalProgress = useCallback((goalData) => {
    return track('goal_progress', {
      goal_id: goalData.goalId,
      goal_type: goalData.type, // 'skill', 'course', 'certification'
      progress_percentage: goalData.progress,
      milestone_reached: goalData.milestone,
      time_to_milestone: goalData.timeToMilestone,
      expected_completion_date: goalData.expectedCompletion,
      current_streak: goalData.streak,
    });
  }, [track]);

  // Error boundary integration
  const handleError = useCallback((error, errorInfo) => {
    trackError(error, {
      ...errorInfo,
      user_id: userId,
      path: pathname,
      privacy_level: getPrivacyLevel(privacyConsent),
    });
  }, [trackError, userId, pathname, privacyConsent]);

  const contextValue = {
    // Core analytics
    analytics,
    isInitialized,
    
    // Privacy
    privacyConsent,
    requestPrivacyConsent,
    
    // Basic tracking
    track,
    trackError: handleError,
    trackPerformance,
    
    // Specialized tracking
    trackCourseView,
    trackCourseEnrollment,
    trackCourseInteraction,
    trackLearningProgress,
    trackLearningSession,
    trackQuiz,
    trackSearch,
    trackRecommendation,
    trackPersonalizationFeedback,
    trackGoalProgress,
    
    // Activity tracking
    startActivity,
    pauseActivity,
    resumeActivity,
    endActivity,
    
    // Configuration
    enableAutoTracking,
    userId,
  };

  return (
    <AnalyticsContext.Provider value={contextValue}>
      {children}
    </AnalyticsContext.Provider>
  );
}

// Hook to use analytics context
export function useAnalyticsContext() {
  const context = useContext(AnalyticsContext);
  if (!context) {
    throw new Error('useAnalyticsContext must be used within an AnalyticsProvider');
  }
  return context;
}

// Utility functions
function getPrivacyLevel(privacySettings) {
  if (!privacySettings) return 'unknown';
  
  if (privacySettings.behavioral_analysis && 
      privacySettings.personalization_consent) {
    return 'full';
  } else if (privacySettings.analytics_consent) {
    return 'analytics';
  } else {
    return 'minimal';
  }
}

// Core Web Vitals tracking
function trackCoreWebVitals() {
  // Track First Input Delay (FID)
  if ('PerformanceObserver' in window) {
    try {
      new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          analytics.trackPerformance('first_input_delay', entry.processingStart - entry.startTime, {
            entry_type: entry.entryType,
            name: entry.name,
          });
        }
      }).observe({ entryTypes: ['first-input'] });

      // Track Largest Contentful Paint (LCP)
      new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        const lastEntry = entries[entries.length - 1];
        analytics.trackPerformance('largest_contentful_paint', lastEntry.startTime, {
          element: lastEntry.element?.tagName || 'unknown',
          size: lastEntry.size,
        });
      }).observe({ entryTypes: ['largest-contentful-paint'] });

      // Track Cumulative Layout Shift (CLS)
      let clsValue = 0;
      new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
          }
        }
        analytics.trackPerformance('cumulative_layout_shift', clsValue);
      }).observe({ entryTypes: ['layout-shift'] });

    } catch (error) {
      console.warn('Could not set up Core Web Vitals tracking:', error);
    }
  }
}

export default AnalyticsProvider;