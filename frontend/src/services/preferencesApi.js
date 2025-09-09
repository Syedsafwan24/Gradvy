/**
 * Preferences API Service
 * Handles all preference-related API calls using RTK Query
 */

import { apiSlice } from '@/store/api/apiSlice';

export const preferencesApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getUserPreferences: builder.query({
      query: () => '/preferences/',
      providesTags: ['UserPreferences'],
      transformErrorResponse: (response) => ({
        status: response.status,
        message: response.data?.error || 'Failed to fetch preferences',
        onboarding_required: response.data?.onboarding_required || false
      })
    }),
    
    createUserPreferences: builder.mutation({
      query: (preferencesData) => ({
        url: '/preferences/',
        method: 'POST',
        body: preferencesData,
      }),
      invalidatesTags: ['UserPreferences'],
      transformResponse: (response) => ({
        success: true,
        data: response,
        message: 'Preferences created successfully'
      })
    }),
    
    updateUserPreferences: builder.mutation({
      query: (preferencesData) => ({
        url: '/preferences/',
        method: 'PUT',
        body: preferencesData,
      }),
      invalidatesTags: ['UserPreferences'],
      transformResponse: (response) => ({
        success: true,
        data: response,
        message: 'Preferences updated successfully'
      })
    }),
    
    partialUpdateUserPreferences: builder.mutation({
      query: (preferencesData) => ({
        url: '/preferences/',
        method: 'PATCH',
        body: preferencesData,
      }),
      invalidatesTags: ['UserPreferences'],
      transformResponse: (response) => ({
        success: true,
        data: response,
        message: 'Preferences updated successfully'
      })
    }),
    
    submitOnboarding: builder.mutation({
      query: (onboardingData) => ({
        url: '/preferences/onboarding/',
        method: 'POST',
        body: onboardingData,
      }),
      invalidatesTags: ['UserPreferences'],
      transformResponse: (response) => ({
        success: true,
        data: response,
        message: response.message || 'Onboarding completed successfully'
      })
    }),
    
    submitQuickOnboarding: builder.mutation({
      query: (quickOnboardingData) => ({
        url: '/preferences/quick-onboarding/',
        method: 'POST',
        body: quickOnboardingData,
      }),
      invalidatesTags: ['UserPreferences'],
      transformResponse: (response) => ({
        success: true,
        data: response,
        message: response.message || 'Quick onboarding completed successfully',
        profile_completion_percentage: response.profile_completion_percentage,
        quick_onboarding_completed: response.quick_onboarding_completed
      }),
      transformErrorResponse: (response) => ({
        status: response.status,
        message: response.data?.error || response.data?.details || 'Failed to complete quick onboarding',
        details: response.data
      })
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
      })
    }),
    
    getUserAnalytics: builder.query({
      query: (timeframe = '30d') => `/preferences/analytics/?timeframe=${timeframe}`,
      providesTags: ['Analytics'],
      transformResponse: (response) => ({
        analytics: response.analytics,
        generated_at: response.generated_at
      })
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
      })
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
      })
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
      })
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
 * Transform frontend preference data to backend format
 */
export const transformPreferenceData = (frontendData) => {
  const transformed = {};

  // Transform basic_info section
  if (frontendData.basic_info) {
    transformed.basic_info = {
      learning_goals: frontendData.basic_info.learning_goals || [],
      experience_level: frontendData.basic_info.experience_level || '',
      preferred_pace: frontendData.basic_info.preferred_pace || '',
      time_availability: frontendData.basic_info.time_availability || '',
      learning_style: frontendData.basic_info.learning_style || [],
      career_stage: frontendData.basic_info.career_stage || '',
      target_timeline: frontendData.basic_info.target_timeline || ''
    };
  }

  // Transform content_preferences section
  if (frontendData.content_preferences) {
    transformed.content_preferences = {
      preferred_platforms: frontendData.content_preferences.preferred_platforms || [],
      content_types: frontendData.content_preferences.content_types || [],
      difficulty_preference: frontendData.content_preferences.difficulty_preference || 'mixed',
      duration_preference: frontendData.content_preferences.duration_preference || 'mixed',
      language_preference: frontendData.content_preferences.language_preference || ['english'],
      instructor_ratings_min: frontendData.content_preferences.instructor_ratings_min || 3.0
    };
  }

  // Pass through custom preferences and other fields
  if (frontendData.custom_preferences) {
    transformed.custom_preferences = frontendData.custom_preferences;
  }

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