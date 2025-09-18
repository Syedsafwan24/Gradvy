/**
 * Preferences API Service
 * Handles all preference-related API calls using RTK Query
 */

import { apiSlice } from '@/store/api/apiSlice';
import { normalizeApiError, extractSuccessData, extractSuccessMessage } from '@/utils/apiErrors';

export const preferencesApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getUserPreferences: builder.query({
      query: () => '/preferences/',
      providesTags: (result, error, arg) => [
        'UserPreferences',
        { type: 'UserPreferences', id: 'CURRENT_USER' },
        { type: 'BasicInfo', id: 'CURRENT_USER' },
        { type: 'ContentPreferences', id: 'CURRENT_USER' },
        { type: 'OnboardingStatus', id: 'CURRENT_USER' }
      ],
      transformResponse: (response) => {
        // Handle standardized success response
        if (response.success === true) {
          return extractSuccessData(response);
        }
        return response;
      },
      transformErrorResponse: (response) => {
        const e = normalizeApiError(response);
        return {
          status: e.status,
          message: e.message,
          fieldErrors: e.fieldErrors,
          code: e.code,
          requestId: e.requestId,
          onboarding_required: response.data?.error?.details?.onboarding_required || false
        };
      }
    }),
    
    createUserPreferences: builder.mutation({
      query: (preferencesData) => ({
        url: '/preferences/',
        method: 'POST',
        body: preferencesData,
      }),
      invalidatesTags: [
        'UserPreferences',
        { type: 'UserPreferences', id: 'CURRENT_USER' },
        { type: 'BasicInfo', id: 'CURRENT_USER' },
        { type: 'ContentPreferences', id: 'CURRENT_USER' },
        { type: 'OnboardingStatus', id: 'CURRENT_USER' }
      ],
      transformResponse: (response) => {
        if (response.success === true) {
          return {
            success: true,
            data: extractSuccessData(response),
            message: extractSuccessMessage(response)
          };
        }
        return {
          success: true,
          data: response,
          message: 'Preferences created successfully'
        };
      },
      transformErrorResponse: (response) => normalizeApiError(response)
    }),

    updateUserPreferences: builder.mutation({
      query: (preferencesData) => ({
        url: '/preferences/',
        method: 'PUT',
        body: preferencesData,
      }),
      invalidatesTags: [
        'UserPreferences',
        { type: 'UserPreferences', id: 'CURRENT_USER' },
        { type: 'BasicInfo', id: 'CURRENT_USER' },
        { type: 'ContentPreferences', id: 'CURRENT_USER' },
        { type: 'OnboardingStatus', id: 'CURRENT_USER' }
      ],
      transformResponse: (response) => {
        if (response.success === true) {
          return {
            success: true,
            data: extractSuccessData(response),
            message: extractSuccessMessage(response)
          };
        }
        return {
          success: true,
          data: response,
          message: 'Preferences updated successfully'
        };
      },
      transformErrorResponse: (response) => normalizeApiError(response)
    }),
    
    partialUpdateUserPreferences: builder.mutation({
      query: (preferencesData) => ({
        url: '/preferences/',
        method: 'PATCH',
        body: preferencesData,
      }),
      invalidatesTags: (result, error, arg) => {
        const tags = ['UserPreferences', { type: 'UserPreferences', id: 'CURRENT_USER' }];

        // Granular invalidation based on updated sections
        if (arg.basic_info) {
          tags.push({ type: 'BasicInfo', id: 'CURRENT_USER' });
        }
        if (arg.content_preferences) {
          tags.push({ type: 'ContentPreferences', id: 'CURRENT_USER' });
        }
        if (arg.onboarding_status) {
          tags.push({ type: 'OnboardingStatus', id: 'CURRENT_USER' });
        }

        return tags;
      },
      // Optimistic update
      async onQueryStarted(patch, { dispatch, queryFulfilled }) {
        const patchResult = dispatch(
          preferencesApi.util.updateQueryData('getUserPreferences', undefined, (draft) => {
            // Apply optimistic updates to the cache
            if (patch.basic_info && draft.basic_info) {
              Object.assign(draft.basic_info, patch.basic_info);
            }
            if (patch.content_preferences && draft.content_preferences) {
              Object.assign(draft.content_preferences, patch.content_preferences);
            }
            if (patch.custom_preferences) {
              Object.assign(draft.custom_preferences, patch.custom_preferences);
            }

            // Update timestamp
            draft.updated_at = new Date().toISOString();
          })
        );

        try {
          await queryFulfilled;
        } catch {
          // Revert optimistic update on error
          patchResult.undo();
        }
      },
      transformResponse: (response) => ({
        success: true,
        data: response,
        message: 'Preferences updated successfully'
      }),
      transformErrorResponse: (response) => normalizeApiError(response)
    }),
    
    submitOnboarding: builder.mutation({
      query: (onboardingData) => ({
        url: '/preferences/onboarding/',
        method: 'POST',
        body: onboardingData,
      }),
      invalidatesTags: [
        'UserPreferences',
        { type: 'UserPreferences', id: 'CURRENT_USER' },
        { type: 'BasicInfo', id: 'CURRENT_USER' },
        { type: 'ContentPreferences', id: 'CURRENT_USER' },
        { type: 'OnboardingStatus', id: 'CURRENT_USER' }
      ],
      transformResponse: (response) => ({
        success: true,
        data: response,
        message: response.message || 'Onboarding completed successfully'
      }),
      transformErrorResponse: (response) => normalizeApiError(response)
    }),

    submitQuickOnboarding: builder.mutation({
      query: (quickOnboardingData) => ({
        url: '/preferences/quick-onboarding/',
        method: 'POST',
        body: quickOnboardingData,
      }),
      invalidatesTags: [
        'UserPreferences',
        { type: 'UserPreferences', id: 'CURRENT_USER' },
        { type: 'BasicInfo', id: 'CURRENT_USER' },
        { type: 'OnboardingStatus', id: 'CURRENT_USER' }
      ],
      transformResponse: (response) => ({
        success: true,
        data: response,
        message: response.message || 'Quick onboarding completed successfully',
        profile_completion_percentage: response.profile_completion_percentage,
        quick_onboarding_completed: response.quick_onboarding_completed
      }),
      transformErrorResponse: (response) => normalizeApiError(response)
    }),
    
    logInteraction: builder.mutation({
      query: (interactionData) => ({
        url: '/preferences/interactions/',
        method: 'POST',
        body: interactionData,
      }),
      transformResponse: (response) => ({
        success: response.success,
        interaction_type: response.interaction_type,
        timestamp: response.timestamp
      }),
      transformErrorResponse: (response) => normalizeApiError(response)
    }),
    
    getUserAnalytics: builder.query({
      query: (timeframe = '30d') => `/preferences/analytics/?timeframe=${timeframe}`,
      providesTags: ['Analytics'],
      transformResponse: (response) => ({
        analytics: response.analytics,
        generated_at: response.generated_at
      }),
      transformErrorResponse: (response) => normalizeApiError(response)
    }),
    
    getPersonalizedRecommendations: builder.query({
      query: (params = {}) => ({
        url: '/preferences/recommendations/',
        params,
      }),
      providesTags: ['Recommendations'],
      transformResponse: (response) => ({
        recommendations: response.recommendations,
        source: response.source,
        message: response.message
      }),
      transformErrorResponse: (response) => normalizeApiError(response)
    }),
    
    generateRecommendations: builder.mutation({
      query: () => ({
        url: '/preferences/recommendations/',
        method: 'POST',
      }),
      invalidatesTags: ['Recommendations'],
      transformResponse: (response) => ({
        success: true,
        recommendations: response.recommendations,
        source: response.source,
        message: response.message || 'Recommendations generated successfully'
      }),
      transformErrorResponse: (response) => normalizeApiError(response)
    }),
    
    getPreferenceChoices: builder.query({
      query: () => '/preferences/choices/',
      transformResponse: (response) => response,
      // Cache for 1 hour since choices don't change often
      keepUnusedDataFor: 3600
    }),

    saveOnboardingProgress: builder.mutation({
      query: (progressData) => ({
        url: '/preferences/onboarding-progress/',
        method: 'POST',
        body: progressData,
      }),
      // Don't invalidate tags for progress saves to avoid refetching
      transformResponse: (response) => ({
        success: true,
        data: response,
        message: 'Progress saved successfully'
      }),
      transformErrorResponse: (response) => normalizeApiError(response)
    })
  }),
});

export const {
  useGetUserPreferencesQuery,
  useCreateUserPreferencesMutation,
  useUpdateUserPreferencesMutation,
  usePartialUpdateUserPreferencesMutation,
  useSubmitOnboardingMutation,
  useSubmitQuickOnboardingMutation,
  useLogInteractionMutation,
  useGetUserAnalyticsQuery,
  useGetPersonalizedRecommendationsQuery,
  useGenerateRecommendationsMutation,
  useGetPreferenceChoicesQuery,
  useSaveOnboardingProgressMutation,
} = preferencesApi;

/**
 * Helper function to save preferences with optimistic updates
 */
export const savePreferencesOptimistically = async (updatedData, dispatch, currentPreferences) => {
  try {
    // Log the interaction first
    dispatch(
      preferencesApi.endpoints.logInteraction.initiate({
        type: 'page_view',
        data: { 
          page: 'preferences_dashboard',
          section: 'update_preferences',
          changes: Object.keys(updatedData)
        },
        context: {
          timestamp: new Date().toISOString(),
          user_agent: navigator.userAgent
        }
      })
    );

    // Determine if this is a partial or full update
    const isPartialUpdate = Object.keys(updatedData).length < 
      Object.keys(currentPreferences || {}).length;

    const mutation = isPartialUpdate ? 
      preferencesApi.endpoints.partialUpdateUserPreferences :
      preferencesApi.endpoints.updateUserPreferences;

    const result = await dispatch(mutation.initiate(updatedData)).unwrap();
    
    return {
      success: true,
      data: result.data,
      message: result.message
    };
  } catch (error) {
    console.error('Failed to save preferences:', error);
    throw {
      success: false,
      message: error?.data?.message || 'Failed to save preferences',
      details: error
    };
  }
};

/**
 * Enhanced interaction logging with automatic context
 */
export const logUserInteraction = (dispatch, interactionType, data = {}, context = {}) => {
  const enrichedContext = {
    timestamp: new Date().toISOString(),
    user_agent: navigator.userAgent,
    screen_resolution: `${screen.width}x${screen.height}`,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    page: window.location.pathname,
    ...context
  };

  try {
    dispatch(
      preferencesApi.endpoints.logInteraction.initiate({
        type: interactionType,
        data,
        context: enrichedContext
      })
    );
  } catch (error) {
    console.warn('Failed to log interaction:', error);
  }
};

/**
 * Retry mechanism for preferences updates with exponential backoff
 */
export const updatePreferencesWithRetry = async (updatedData, dispatch, maxRetries = 3) => {
  let attempt = 0;
  let lastError = null;

  while (attempt < maxRetries) {
    try {
      const result = await dispatch(
        preferencesApi.endpoints.partialUpdateUserPreferences.initiate(updatedData)
      ).unwrap();

      return {
        success: true,
        data: result.data,
        message: result.message,
        attempts: attempt + 1
      };
    } catch (error) {
      lastError = error;
      attempt++;

      // Don't retry on validation errors (4xx), only on network/server errors
      if (error?.status && error.status >= 400 && error.status < 500) {
        throw {
          success: false,
          message: error?.data?.message || 'Validation error',
          details: error,
          attempts: attempt
        };
      }

      if (attempt < maxRetries) {
        // Exponential backoff: 1s, 2s, 4s
        const delay = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));

        console.log(`Retrying preferences update... Attempt ${attempt + 1}/${maxRetries}`);
      }
    }
  }

  throw {
    success: false,
    message: lastError?.data?.message || 'Failed to save preferences after multiple attempts',
    details: lastError,
    attempts: attempt
  };
};

/**
 * Transform frontend preference data to backend format
 */
export const transformPreferenceData = (frontendData) => {
  const transformed = {};

  // Transform basic_info section
  if (frontendData.basic_info) {
    transformed.basic_info = {
      learning_goals: Array.isArray(frontendData.basic_info.learning_goals)
        ? frontendData.basic_info.learning_goals
        : [],
      experience_level: frontendData.basic_info.experience_level || '',
      preferred_pace: frontendData.basic_info.preferred_pace || '',
      time_availability: frontendData.basic_info.time_availability || '',
      learning_style: Array.isArray(frontendData.basic_info.learning_style)
        ? frontendData.basic_info.learning_style
        : [],
      career_stage: frontendData.basic_info.career_stage || '',
      target_timeline: frontendData.basic_info.target_timeline || ''
    };
  }

  // Transform content_preferences section
  if (frontendData.content_preferences) {
    transformed.content_preferences = {
      preferred_platforms: Array.isArray(frontendData.content_preferences.preferred_platforms)
        ? frontendData.content_preferences.preferred_platforms
        : [],
      content_types: Array.isArray(frontendData.content_preferences.content_types)
        ? frontendData.content_preferences.content_types
        : [],
      difficulty_preference: frontendData.content_preferences.difficulty_preference || 'mixed',
      duration_preference: frontendData.content_preferences.duration_preference || 'mixed',
      language_preference: Array.isArray(frontendData.content_preferences.language_preference)
        ? frontendData.content_preferences.language_preference
        : ['english'],
      instructor_ratings_min: typeof frontendData.content_preferences.instructor_ratings_min === 'number'
        ? frontendData.content_preferences.instructor_ratings_min
        : 3.0
    };
  }

  // Handle onboarding status fields
  if (frontendData.onboarding_status !== undefined) {
    transformed.onboarding_status = frontendData.onboarding_status;
  }

  // Handle quick onboarding data
  if (frontendData.quick_onboarding_data) {
    transformed.quick_onboarding_data = frontendData.quick_onboarding_data;
  }

  // Pass through custom preferences and other top-level fields
  if (frontendData.custom_preferences) {
    transformed.custom_preferences = frontendData.custom_preferences;
  }

  // Handle gamification fields
  if (frontendData.achievement_badges) {
    transformed.achievement_badges = Array.isArray(frontendData.achievement_badges)
      ? frontendData.achievement_badges
      : [];
  }

  if (frontendData.completion_milestones) {
    transformed.completion_milestones = frontendData.completion_milestones;
  }

  if (frontendData.streak_data) {
    transformed.streak_data = frontendData.streak_data;
  }

  // Filter out null/undefined values to avoid sending unnecessary data
  Object.keys(transformed).forEach(key => {
    if (transformed[key] === null || transformed[key] === undefined) {
      delete transformed[key];
    }
  });

  return transformed;
};

/**
 * Calculate preference completion percentage
 */
export const calculatePreferenceCompletion = (preferences) => {
  if (!preferences) return 0;

  const totalFields = 12; // Adjust based on total preference fields
  let completedFields = 0;

  // Check basic_info completion
  if (preferences.basic_info) {
    const basicInfo = preferences.basic_info;
    if (basicInfo.learning_goals?.length > 0) completedFields++;
    if (basicInfo.experience_level) completedFields++;
    if (basicInfo.preferred_pace) completedFields++;
    if (basicInfo.time_availability) completedFields++;
    if (basicInfo.learning_style?.length > 0) completedFields++;
    if (basicInfo.career_stage) completedFields++;
    if (basicInfo.target_timeline) completedFields++;
  }

  // Check content_preferences completion
  if (preferences.content_preferences) {
    const contentPrefs = preferences.content_preferences;
    if (contentPrefs.preferred_platforms?.length > 0) completedFields++;
    if (contentPrefs.content_types?.length > 0) completedFields++;
    if (contentPrefs.difficulty_preference) completedFields++;
    if (contentPrefs.duration_preference) completedFields++;
    if (contentPrefs.language_preference?.length > 0) completedFields++;
  }

  return Math.round((completedFields / totalFields) * 100);
};

/**
 * Debug utilities for preferences sync issues
 */
export const preferencesDebugUtils = {
  /**
   * Log detailed cache state for debugging
   */
  logCacheState: (getState) => {
    const apiState = getState().api;
    const preferencesQueries = apiState.queries['getUserPreferences(undefined)'];

    console.group('🔍 Preferences Cache State');
    console.log('Cache Status:', preferencesQueries?.status);
    console.log('Last Fetched:', preferencesQueries?.fulfilledTimeStamp ? new Date(preferencesQueries.fulfilledTimeStamp) : 'Never');
    console.log('Data Present:', !!preferencesQueries?.data);
    console.log('Error:', preferencesQueries?.error);
    console.groupEnd();
  },

  /**
   * Validate data consistency between cache and component state
   */
  validateDataConsistency: (cacheData, componentData) => {
    const issues = [];

    if (!cacheData && componentData) {
      issues.push('Component has data but cache is empty');
    }

    if (cacheData && !componentData) {
      issues.push('Cache has data but component is empty');
    }

    if (cacheData && componentData) {
      // Check timestamp consistency
      if (cacheData.updated_at !== componentData.updated_at) {
        issues.push(`Timestamp mismatch: Cache=${cacheData.updated_at}, Component=${componentData.updated_at}`);
      }

      // Check onboarding status consistency
      if (cacheData.onboarding_status !== componentData.onboarding_status) {
        issues.push(`Onboarding status mismatch: Cache=${cacheData.onboarding_status}, Component=${componentData.onboarding_status}`);
      }
    }

    if (issues.length > 0) {
      console.group('⚠️ Data Consistency Issues');
      issues.forEach(issue => console.warn(issue));
      console.groupEnd();
    }

    return issues;
  },

  /**
   * Log preferences update flow for debugging
   */
  logUpdateFlow: (phase, data = {}) => {
    const timestamp = new Date().toISOString();
    console.log(`🔄 [${timestamp}] Preferences Update - ${phase}:`, data);
  },

  /**
   * Validate transform function output
   */
  validateTransformOutput: (input, output) => {
    const issues = [];

    // Check for required fields in basic_info
    if (input.basic_info && output.basic_info) {
      const requiredFields = ['learning_goals', 'experience_level', 'learning_style'];
      requiredFields.forEach(field => {
        if (input.basic_info[field] && !output.basic_info[field]) {
          issues.push(`Missing ${field} in transformed basic_info`);
        }
      });
    }

    // Check for required fields in content_preferences
    if (input.content_preferences && output.content_preferences) {
      const requiredFields = ['preferred_platforms', 'content_types'];
      requiredFields.forEach(field => {
        if (input.content_preferences[field] && !output.content_preferences[field]) {
          issues.push(`Missing ${field} in transformed content_preferences`);
        }
      });
    }

    if (issues.length > 0) {
      console.group('⚠️ Transform Validation Issues');
      console.log('Input:', input);
      console.log('Output:', output);
      issues.forEach(issue => console.warn(issue));
      console.groupEnd();
    }

    return issues;
  }
};

/**
 * Enhanced preference validation
 */
export const validatePreferencesData = (preferences) => {
  const validation = {
    isValid: true,
    errors: [],
    warnings: []
  };

  if (!preferences) {
    validation.isValid = false;
    validation.errors.push('Preferences data is null or undefined');
    return validation;
  }

  // Validate basic_info structure
  if (preferences.basic_info) {
    const basicInfo = preferences.basic_info;

    if (basicInfo.learning_goals && !Array.isArray(basicInfo.learning_goals)) {
      validation.errors.push('learning_goals must be an array');
    }

    if (basicInfo.learning_style && !Array.isArray(basicInfo.learning_style)) {
      validation.errors.push('learning_style must be an array');
    }

    if (basicInfo.experience_level && !['complete_beginner', 'some_basics', 'intermediate', 'advanced'].includes(basicInfo.experience_level)) {
      validation.warnings.push(`Unknown experience_level: ${basicInfo.experience_level}`);
    }
  }

  // Validate content_preferences structure
  if (preferences.content_preferences) {
    const contentPrefs = preferences.content_preferences;

    if (contentPrefs.preferred_platforms && !Array.isArray(contentPrefs.preferred_platforms)) {
      validation.errors.push('preferred_platforms must be an array');
    }

    if (contentPrefs.content_types && !Array.isArray(contentPrefs.content_types)) {
      validation.errors.push('content_types must be an array');
    }

    if (contentPrefs.instructor_ratings_min && (typeof contentPrefs.instructor_ratings_min !== 'number' || contentPrefs.instructor_ratings_min < 0 || contentPrefs.instructor_ratings_min > 5)) {
      validation.errors.push('instructor_ratings_min must be a number between 0 and 5');
    }
  }

  // Validate onboarding status
  if (preferences.onboarding_status && !['not_started', 'quick_completed', 'full_completed'].includes(preferences.onboarding_status)) {
    validation.warnings.push(`Unknown onboarding_status: ${preferences.onboarding_status}`);
  }

  if (validation.errors.length > 0) {
    validation.isValid = false;
  }

  return validation;
};
