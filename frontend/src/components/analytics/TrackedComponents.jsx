/**
 * Tracked Component Wrappers
 * These components automatically add analytics tracking to common UI elements
 */

'use client';

import { forwardRef, useCallback, useRef, useEffect } from 'react';
import { useAnalyticsContext } from './AnalyticsProvider';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';

// Tracked Button Component
export const TrackedButton = forwardRef(({ 
  onClick, 
  children, 
  trackingName,
  trackingContext = {},
  trackingOptions = {},
  className,
  ...props 
}, ref) => {
  const { track } = useAnalyticsContext();

  const handleClick = useCallback((event) => {
    // Track the button click
    track('button_click', {
      button_name: trackingName || children?.toString() || 'unknown',
      button_text: children?.toString(),
      button_context: trackingContext,
      click_position: {
        x: event.clientX,
        y: event.clientY,
      },
      page_url: window.location.href,
      ...trackingOptions.properties
    }, trackingOptions);

    // Call the original onClick handler
    if (onClick) {
      onClick(event);
    }
  }, [onClick, track, trackingName, children, trackingContext, trackingOptions]);

  return (
    <Button
      ref={ref}
      onClick={handleClick}
      className={className}
      {...props}
    >
      {children}
    </Button>
  );
});

TrackedButton.displayName = 'TrackedButton';

// Tracked Link Component
export const TrackedLink = forwardRef(({ 
  href, 
  onClick, 
  children, 
  trackingName,
  trackingContext = {},
  trackingOptions = {},
  className,
  external = false,
  ...props 
}, ref) => {
  const { track } = useAnalyticsContext();

  const handleClick = useCallback((event) => {
    // Track the link click
    track('link_click', {
      link_url: href,
      link_text: children?.toString(),
      link_name: trackingName || children?.toString() || href,
      link_context: trackingContext,
      external_link: external,
      click_position: {
        x: event.clientX,
        y: event.clientY,
      },
      ...trackingOptions.properties
    }, trackingOptions);

    // Call the original onClick handler
    if (onClick) {
      onClick(event);
    }
  }, [onClick, track, href, trackingName, children, trackingContext, trackingOptions, external]);

  const LinkComponent = external ? 'a' : 'a'; // You might want to use Next.js Link here

  return (
    <LinkComponent
      ref={ref}
      href={href}
      onClick={handleClick}
      className={className}
      {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
      {...props}
    >
      {children}
    </LinkComponent>
  );
});

TrackedLink.displayName = 'TrackedLink';

// Tracked Input Component with focus/blur tracking
export const TrackedInput = forwardRef(({ 
  onFocus, 
  onBlur, 
  onChange,
  trackingName,
  trackingContext = {},
  trackingOptions = {},
  ...props 
}, ref) => {
  const { track } = useAnalyticsContext();
  const focusTimeRef = useRef(null);
  const valueChangesRef = useRef(0);

  const handleFocus = useCallback((event) => {
    focusTimeRef.current = Date.now();
    valueChangesRef.current = 0;

    track('input_focus', {
      input_name: trackingName || event.target.name || event.target.id || 'unknown',
      input_type: event.target.type,
      input_context: trackingContext,
      ...trackingOptions.properties
    }, trackingOptions);

    if (onFocus) {
      onFocus(event);
    }
  }, [onFocus, track, trackingName, trackingContext, trackingOptions]);

  const handleBlur = useCallback((event) => {
    const focusTime = focusTimeRef.current ? Date.now() - focusTimeRef.current : 0;

    track('input_blur', {
      input_name: trackingName || event.target.name || event.target.id || 'unknown',
      input_type: event.target.type,
      focus_time: focusTime,
      value_changes: valueChangesRef.current,
      final_value_length: event.target.value?.length || 0,
      input_context: trackingContext,
      ...trackingOptions.properties
    }, trackingOptions);

    if (onBlur) {
      onBlur(event);
    }
  }, [onBlur, track, trackingName, trackingContext, trackingOptions]);

  const handleChange = useCallback((event) => {
    valueChangesRef.current += 1;

    if (onChange) {
      onChange(event);
    }
  }, [onChange]);

  return (
    <Input
      ref={ref}
      onFocus={handleFocus}
      onBlur={handleBlur}
      onChange={handleChange}
      {...props}
    />
  );
});

TrackedInput.displayName = 'TrackedInput';

// Tracked Card Component for course/content cards
export const TrackedCard = forwardRef(({ 
  children, 
  onClick,
  trackingName,
  trackingContext = {},
  trackingOptions = {},
  contentId,
  contentType = 'card',
  ...props 
}, ref) => {
  const { track } = useAnalyticsContext();
  const viewTimeRef = useRef(null);
  const cardRef = useRef(null);

  // Track card view when it comes into viewport
  useEffect(() => {
    const card = cardRef.current;
    if (!card) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            viewTimeRef.current = Date.now();
            track('card_view', {
              card_name: trackingName || contentId || 'unknown',
              content_id: contentId,
              content_type: contentType,
              card_context: trackingContext,
              viewport_percentage: Math.round(entry.intersectionRatio * 100),
              ...trackingOptions.properties
            }, trackingOptions);
          } else if (viewTimeRef.current) {
            const viewTime = Date.now() - viewTimeRef.current;
            track('card_view_end', {
              card_name: trackingName || contentId || 'unknown',
              content_id: contentId,
              view_duration: viewTime,
              card_context: trackingContext,
            });
            viewTimeRef.current = null;
          }
        });
      },
      { threshold: [0.1, 0.5, 0.9] }
    );

    observer.observe(card);

    return () => {
      observer.disconnect();
      if (viewTimeRef.current) {
        const viewTime = Date.now() - viewTimeRef.current;
        track('card_view_end', {
          card_name: trackingName || contentId || 'unknown',
          content_id: contentId,
          view_duration: viewTime,
          card_context: trackingContext,
        });
      }
    };
  }, [track, trackingName, contentId, contentType, trackingContext, trackingOptions]);

  const handleClick = useCallback((event) => {
    const viewTime = viewTimeRef.current ? Date.now() - viewTimeRef.current : 0;

    track('card_click', {
      card_name: trackingName || contentId || 'unknown',
      content_id: contentId,
      content_type: contentType,
      view_time_before_click: viewTime,
      click_position: {
        x: event.clientX,
        y: event.clientY,
      },
      card_context: trackingContext,
      ...trackingOptions.properties
    }, trackingOptions);

    if (onClick) {
      onClick(event);
    }
  }, [onClick, track, trackingName, contentId, contentType, trackingContext, trackingOptions]);

  return (
    <Card
      ref={(node) => {
        cardRef.current = node;
        if (ref) {
          if (typeof ref === 'function') {
            ref(node);
          } else {
            ref.current = node;
          }
        }
      }}
      onClick={handleClick}
      {...props}
    >
      {children}
    </Card>
  );
});

TrackedCard.displayName = 'TrackedCard';

// Tracked Form Component
export const TrackedForm = forwardRef(({ 
  onSubmit, 
  children, 
  trackingName,
  trackingContext = {},
  trackingOptions = {},
  ...props 
}, ref) => {
  const { track } = useAnalyticsContext();
  const formStartTimeRef = useRef(null);
  const fieldInteractionsRef = useRef({});

  useEffect(() => {
    formStartTimeRef.current = Date.now();
    
    track('form_start', {
      form_name: trackingName || 'unknown',
      form_context: trackingContext,
      field_count: props.children ? React.Children.count(props.children) : 0,
      ...trackingOptions.properties
    }, trackingOptions);
  }, [track, trackingName, trackingContext, trackingOptions, props.children]);

  const handleSubmit = useCallback((event) => {
    const formTime = formStartTimeRef.current ? Date.now() - formStartTimeRef.current : 0;
    const fieldCount = Object.keys(fieldInteractionsRef.current).length;

    track('form_submit', {
      form_name: trackingName || 'unknown',
      form_completion_time: formTime,
      fields_interacted: fieldCount,
      field_interactions: fieldInteractionsRef.current,
      form_context: trackingContext,
      is_successful: !event.defaultPrevented,
      ...trackingOptions.properties
    }, trackingOptions);

    if (onSubmit) {
      onSubmit(event);
    }
  }, [onSubmit, track, trackingName, trackingContext, trackingOptions]);

  const handleFieldInteraction = useCallback((fieldName, interactionType) => {
    if (!fieldInteractionsRef.current[fieldName]) {
      fieldInteractionsRef.current[fieldName] = {
        focus_count: 0,
        change_count: 0,
        first_interaction: Date.now(),
      };
    }

    fieldInteractionsRef.current[fieldName][`${interactionType}_count`] += 1;
    fieldInteractionsRef.current[fieldName].last_interaction = Date.now();
  }, []);

  return (
    <form
      ref={ref}
      onSubmit={handleSubmit}
      {...props}
    >
      {children}
    </form>
  );
});

TrackedForm.displayName = 'TrackedForm';

// Course-specific tracked components
export const TrackedCourseCard = forwardRef(({ 
  courseId, 
  courseData = {},
  onEnroll,
  onView,
  onBookmark,
  children,
  ...props 
}, ref) => {
  const { trackCourseView, trackCourseInteraction } = useAnalyticsContext();

  const handleView = useCallback(() => {
    trackCourseView(courseId, courseData);
    if (onView) {
      onView();
    }
  }, [trackCourseView, courseId, courseData, onView]);

  const handleEnroll = useCallback((event) => {
    trackCourseInteraction(courseId, 'enroll', {
      ...courseData,
      enrollment_method: 'card_click',
    });
    if (onEnroll) {
      onEnroll(event);
    }
  }, [trackCourseInteraction, courseId, courseData, onEnroll]);

  const handleBookmark = useCallback((event) => {
    trackCourseInteraction(courseId, 'bookmark', courseData);
    if (onBookmark) {
      onBookmark(event);
    }
  }, [trackCourseInteraction, courseId, courseData, onBookmark]);

  return (
    <TrackedCard
      ref={ref}
      trackingName={`course_${courseId}`}
      trackingContext={{
        course_id: courseId,
        course_title: courseData.title,
        course_category: courseData.category,
        course_provider: courseData.provider,
      }}
      contentId={courseId}
      contentType="course"
      onClick={handleView}
      {...props}
    >
      {children}
      {/* You could add automatic tracking buttons here */}
    </TrackedCard>
  );
});

TrackedCourseCard.displayName = 'TrackedCourseCard';

// Search component with automatic tracking
export const TrackedSearchInput = forwardRef(({ 
  onSearch, 
  onResults,
  placeholder = "Search courses...",
  trackingName = "main_search",
  ...props 
}, ref) => {
  const { trackSearch } = useAnalyticsContext();
  const searchTimeRef = useRef(null);

  const handleSearch = useCallback((query) => {
    const searchTime = searchTimeRef.current ? Date.now() - searchTimeRef.current : 0;
    
    trackSearch({
      query: query,
      search_source: trackingName,
      time_to_search: searchTime,
    });

    if (onSearch) {
      onSearch(query);
    }
  }, [trackSearch, trackingName, onSearch]);

  const handleInputChange = useCallback((event) => {
    if (!searchTimeRef.current && event.target.value) {
      searchTimeRef.current = Date.now();
    }
  }, []);

  return (
    <TrackedInput
      ref={ref}
      placeholder={placeholder}
      trackingName={trackingName}
      onChange={handleInputChange}
      onKeyPress={(event) => {
        if (event.key === 'Enter') {
          handleSearch(event.target.value);
        }
      }}
      {...props}
    />
  );
});

TrackedSearchInput.displayName = 'TrackedSearchInput';

// Video player with comprehensive tracking
export const TrackedVideoPlayer = forwardRef(({ 
  videoId,
  videoData = {},
  src,
  onPlay,
  onPause,
  onEnded,
  onTimeUpdate,
  children,
  ...props 
}, ref) => {
  const { track, startActivity, endActivity } = useAnalyticsContext();
  const watchSegments = useRef([]);
  const currentSegmentStart = useRef(null);

  const handlePlay = useCallback((event) => {
    currentSegmentStart.current = event.target.currentTime;
    startActivity(`video_${videoId}`, 'video_watch', {
      video_id: videoId,
      video_title: videoData.title,
      video_duration: event.target.duration,
    });

    track('video_play', {
      video_id: videoId,
      timestamp: event.target.currentTime,
      playback_rate: event.target.playbackRate,
      video_context: videoData,
    });

    if (onPlay) {
      onPlay(event);
    }
  }, [track, startActivity, videoId, videoData, onPlay]);

  const handlePause = useCallback((event) => {
    if (currentSegmentStart.current !== null) {
      watchSegments.current.push({
        start: currentSegmentStart.current,
        end: event.target.currentTime,
        duration: event.target.currentTime - currentSegmentStart.current,
      });
      currentSegmentStart.current = null;
    }

    track('video_pause', {
      video_id: videoId,
      timestamp: event.target.currentTime,
      completion_rate: event.target.duration ? event.target.currentTime / event.target.duration : 0,
      watch_segments: watchSegments.current.length,
    });

    if (onPause) {
      onPause(event);
    }
  }, [track, videoId, onPause]);

  const handleEnded = useCallback((event) => {
    const totalWatchTime = watchSegments.current.reduce((total, segment) => total + segment.duration, 0);
    
    endActivity(`video_${videoId}`, {
      completion_rate: 1.0,
      total_watch_time: totalWatchTime,
      video_duration: event.target.duration,
      segments_watched: watchSegments.current.length,
    });

    track('video_complete', {
      video_id: videoId,
      total_watch_time: totalWatchTime,
      video_duration: event.target.duration,
      watch_percentage: 100,
      segments_watched: watchSegments.current.length,
    });

    if (onEnded) {
      onEnded(event);
    }
  }, [track, endActivity, videoId, onEnded]);

  return (
    <video
      ref={ref}
      src={src}
      onPlay={handlePlay}
      onPause={handlePause}
      onEnded={handleEnded}
      {...props}
    >
      {children}
    </video>
  );
});

TrackedVideoPlayer.displayName = 'TrackedVideoPlayer';

export {
  TrackedButton,
  TrackedLink,
  TrackedInput,
  TrackedCard,
  TrackedForm,
  TrackedCourseCard,
  TrackedSearchInput,
  TrackedVideoPlayer,
};