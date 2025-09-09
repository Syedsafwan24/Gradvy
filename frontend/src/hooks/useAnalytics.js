/**
 * React hook for GradvyAnalytics integration
 * Provides easy-to-use analytics functionality for React components
 */

import { useEffect, useCallback, useRef, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import analytics from '@/services/analytics';

export function useAnalytics() {
  const router = useRouter();
  const elementRefs = useRef(new Map());
  const activityTimers = useRef(new Map());
  
  // Track component mount/unmount
  useEffect(() => {
    return () => {
      // Clean up any active timers when component unmounts
      activityTimers.current.forEach((timerId, activityId) => {
        analytics.endActivityTimer(activityId);
      });
    };
  }, []);

  // Core tracking methods
  const track = useCallback((eventType, properties = {}, options = {}) => {
    return analytics.track(eventType, properties, options);
  }, []);

  // Specialized tracking methods
  const trackClick = useCallback((element, additionalProps = {}) => {
    const elementInfo = {
      element_type: element.tagName?.toLowerCase(),
      element_id: element.id,
      element_class: element.className,
      element_text: element.textContent?.substring(0, 100),
      element_href: element.href,
      ...additionalProps
    };

    return analytics.trackUserEngagement('click', elementInfo);
  }, []);

  const trackCourseView = useCallback((courseId, courseData = {}) => {
    return analytics.trackCourseInteraction(courseId, 'view', {
      course_title: courseData.title,
      course_category: courseData.category,
      course_difficulty: courseData.difficulty,
      course_duration: courseData.duration,
      course_rating: courseData.rating,
    });
  }, []);

  const trackCourseEnrollment = useCallback((courseId, courseData = {}) => {
    return analytics.trackCourseInteraction(courseId, 'enroll', {
      enrollment_method: courseData.enrollmentMethod || 'direct',
      course_price: courseData.price,
      discount_applied: courseData.discount,
    });
  }, []);

  const trackLearningProgress = useCallback((activityId, progress) => {
    return analytics.trackLearningActivity('progress_update', {
      activity_id: activityId,
      progress_percentage: progress.percentage,
      time_spent: progress.timeSpent,
      current_section: progress.currentSection,
      completion_rate: progress.completionRate,
    });
  }, []);

  const trackQuiz = useCallback((quizId, results) => {
    return analytics.trackQuizAttempt(quizId, {
      score: results.score,
      time_taken: results.timeTaken,
      attempts: results.attempts,
      total_questions: results.totalQuestions,
      correct_answers: results.correctAnswers,
      difficulty: results.difficulty,
      question_types: results.questionTypes,
    });
  }, []);

  const trackSearch = useCallback((searchData) => {
    return analytics.trackSearch(searchData.query, {
      results_count: searchData.resultsCount,
      filters: searchData.filters,
      search_category: searchData.category,
      search_source: searchData.source,
      time_to_results: searchData.timeToResults,
    });
  }, []);

  const trackRecommendation = useCallback((recommendationType, recommendationData) => {
    return analytics.trackPersonalizationEvent(recommendationType, {
      recommendation_id: recommendationData.id,
      algorithm_version: recommendationData.algorithmVersion,
      recommendation_score: recommendationData.score,
      recommendation_reason: recommendationData.reason,
      user_segment: recommendationData.userSegment,
    });
  }, []);

  // Activity timing methods
  const startActivity = useCallback((activityId, activityType, metadata = {}) => {
    analytics.startActivityTimer(activityId, activityType);
    activityTimers.current.set(activityId, {
      type: activityType,
      startTime: Date.now(),
      metadata
    });
  }, []);

  const pauseActivity = useCallback((activityId) => {
    analytics.pauseActivityTimer(activityId);
    const timer = activityTimers.current.get(activityId);
    if (timer) {
      timer.pausedAt = Date.now();
    }
  }, []);

  const resumeActivity = useCallback((activityId) => {
    analytics.resumeActivityTimer(activityId);
    const timer = activityTimers.current.get(activityId);
    if (timer && timer.pausedAt) {
      delete timer.pausedAt;
    }
  }, []);

  const endActivity = useCallback((activityId, completionData = {}) => {
    analytics.endActivityTimer(activityId, completionData);
    activityTimers.current.delete(activityId);
  }, []);

  // Element tracking utilities
  const trackElementInteraction = useCallback((ref, eventType = 'click', additionalProps = {}) => {
    useEffect(() => {
      const element = ref.current;
      if (!element) return;

      const handleInteraction = (event) => {
        trackClick(element, {
          event_type: eventType,
          mouse_x: event.clientX,
          mouse_y: event.clientY,
          ...additionalProps
        });
      };

      element.addEventListener(eventType, handleInteraction);
      
      return () => {
        element.removeEventListener(eventType, handleInteraction);
      };
    }, [ref, eventType, additionalProps]);
  }, [trackClick]);

  // Scroll tracking
  const trackScrollDepth = useCallback((thresholds = [25, 50, 75, 90, 100]) => {
    useEffect(() => {
      let maxScrollDepth = 0;
      const trackedThresholds = new Set();

      const handleScroll = () => {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollDepth = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;

        maxScrollDepth = Math.max(maxScrollDepth, scrollDepth);

        // Track threshold crossings
        thresholds.forEach(threshold => {
          if (scrollDepth >= threshold && !trackedThresholds.has(threshold)) {
            trackedThresholds.add(threshold);
            track('scroll_depth', {
              depth_percentage: threshold,
              page_url: window.location.href,
              time_to_depth: Date.now()
            });
          }
        });
      };

      const throttledScroll = throttle(handleScroll, 250);
      window.addEventListener('scroll', throttledScroll, { passive: true });

      return () => {
        window.removeEventListener('scroll', throttledScroll);
        
        // Track final scroll depth
        if (maxScrollDepth > 0) {
          track('final_scroll_depth', {
            max_depth_percentage: Math.round(maxScrollDepth),
            page_url: window.location.href
          });
        }
      };
    }, [thresholds, track]);
  }, [track]);

  // Form tracking
  const trackFormInteraction = useCallback((formRef, formName) => {
    useEffect(() => {
      const form = formRef.current;
      if (!form) return;

      const startTime = Date.now();
      const fieldInteractions = {};

      const handleFieldFocus = (event) => {
        const fieldName = event.target.name || event.target.id;
        if (fieldName) {
          fieldInteractions[fieldName] = {
            ...fieldInteractions[fieldName],
            focus_time: Date.now(),
            focus_count: (fieldInteractions[fieldName]?.focus_count || 0) + 1
          };
        }
      };

      const handleFieldBlur = (event) => {
        const fieldName = event.target.name || event.target.id;
        if (fieldName && fieldInteractions[fieldName]?.focus_time) {
          const focusTime = Date.now() - fieldInteractions[fieldName].focus_time;
          fieldInteractions[fieldName].total_focus_time = 
            (fieldInteractions[fieldName].total_focus_time || 0) + focusTime;
        }
      };

      const handleFormSubmit = (event) => {
        const totalTime = Date.now() - startTime;
        const fieldCount = Object.keys(fieldInteractions).length;
        
        track('form_submit', {
          form_name: formName,
          total_time: totalTime,
          field_count: fieldCount,
          field_interactions: fieldInteractions,
          is_successful: !event.defaultPrevented
        });
      };

      // Add event listeners
      form.addEventListener('focusin', handleFieldFocus);
      form.addEventListener('focusout', handleFieldBlur);
      form.addEventListener('submit', handleFormSubmit);

      // Track form start
      track('form_start', {
        form_name: formName,
        field_count: form.elements.length
      });

      return () => {
        form.removeEventListener('focusin', handleFieldFocus);
        form.removeEventListener('focusout', handleFieldBlur);
        form.removeEventListener('submit', handleFormSubmit);
      };
    }, [formRef, formName, track]);
  }, [track]);

  // Video tracking
  const trackVideoInteraction = useCallback((videoRef, videoId) => {
    useEffect(() => {
      const video = videoRef.current;
      if (!video) return;

      let watchTime = 0;
      let lastTime = 0;
      const watchSegments = [];
      let currentSegmentStart = null;

      const handlePlay = () => {
        currentSegmentStart = video.currentTime;
        track('video_play', {
          video_id: videoId,
          timestamp: video.currentTime,
          playback_rate: video.playbackRate
        });
      };

      const handlePause = () => {
        if (currentSegmentStart !== null) {
          const segmentDuration = video.currentTime - currentSegmentStart;
          watchSegments.push({
            start: currentSegmentStart,
            end: video.currentTime,
            duration: segmentDuration
          });
          watchTime += segmentDuration;
          currentSegmentStart = null;
        }

        track('video_pause', {
          video_id: videoId,
          timestamp: video.currentTime,
          watch_time: watchTime,
          completion_rate: video.duration ? video.currentTime / video.duration : 0
        });
      };

      const handleEnded = () => {
        if (currentSegmentStart !== null) {
          const segmentDuration = video.currentTime - currentSegmentStart;
          watchTime += segmentDuration;
        }

        track('video_complete', {
          video_id: videoId,
          total_watch_time: watchTime,
          video_duration: video.duration,
          watch_percentage: video.duration ? (watchTime / video.duration) * 100 : 100,
          segments_watched: watchSegments.length,
          completion_rate: 1.0
        });
      };

      const handleTimeUpdate = throttle(() => {
        // Track significant jumps (seeking)
        if (Math.abs(video.currentTime - lastTime) > 5) {
          track('video_seek', {
            video_id: videoId,
            from_timestamp: lastTime,
            to_timestamp: video.currentTime,
            seek_direction: video.currentTime > lastTime ? 'forward' : 'backward'
          });
        }
        lastTime = video.currentTime;
      }, 1000);

      video.addEventListener('play', handlePlay);
      video.addEventListener('pause', handlePause);
      video.addEventListener('ended', handleEnded);
      video.addEventListener('timeupdate', handleTimeUpdate);

      return () => {
        video.removeEventListener('play', handlePlay);
        video.removeEventListener('pause', handlePause);
        video.removeEventListener('ended', handleEnded);
        video.removeEventListener('timeupdate', handleTimeUpdate);
      };
    }, [videoRef, videoId, track]);
  }, [track]);

  // Performance tracking
  const trackPerformance = useCallback((metricName, value, additionalProps = {}) => {
    track('performance_metric', {
      metric_name: metricName,
      metric_value: value,
      page_url: window.location.href,
      timestamp: Date.now(),
      ...additionalProps
    });
  }, [track]);

  // Error boundary integration
  const trackError = useCallback((error, errorInfo = {}) => {
    analytics.trackErrorEvent(error, {
      component_stack: errorInfo.componentStack,
      error_boundary: errorInfo.errorBoundary,
      user_agent: navigator.userAgent,
      url: window.location.href,
    });
  }, []);

  // Memoized analytics instance for direct access
  const analyticsInstance = useMemo(() => analytics, []);

  return {
    // Core tracking
    track,
    trackClick,
    
    // Specialized tracking
    trackCourseView,
    trackCourseEnrollment,
    trackLearningProgress,
    trackQuiz,
    trackSearch,
    trackRecommendation,
    
    // Activity tracking
    startActivity,
    pauseActivity,
    resumeActivity,
    endActivity,
    
    // Utility hooks
    trackElementInteraction,
    trackScrollDepth,
    trackFormInteraction,
    trackVideoInteraction,
    
    // Performance and errors
    trackPerformance,
    trackError,
    
    // Direct access to analytics instance
    analytics: analyticsInstance,
    
    // Helper methods
    setUserId: analyticsInstance.setUserId.bind(analyticsInstance),
    updatePrivacySettings: analyticsInstance.updatePrivacySettings.bind(analyticsInstance),
  };
}

// Utility function for throttling
function throttle(func, limit) {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

export default useAnalytics;