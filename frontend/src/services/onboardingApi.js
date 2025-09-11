/**
 * Onboarding API Service
 * Handles submission of onboarding data to backend
 */

import { apiSlice } from '@/store/api/apiSlice';

export const onboardingApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    submitOnboarding: builder.mutation({
      query: (onboardingData) => ({
        url: '/preferences/onboarding/',
        method: 'POST',
        body: onboardingData,
      }),
      invalidatesTags: ['UserPreferences'],
    }),
    
    getUserPreferences: builder.query({
      query: () => '/preferences/',
      providesTags: ['UserPreferences'],
    }),
    
    updateUserPreferences: builder.mutation({
      query: (preferences) => ({
        url: '/preferences/',
        method: 'PUT',
        body: preferences,
      }),
      invalidatesTags: ['UserPreferences'],
    }),
    
    logInteraction: builder.mutation({
      query: (interactionData) => ({
        url: '/preferences/interactions/',
        method: 'POST',
        body: interactionData,
      }),
    }),
    
    getRecommendations: builder.query({
      query: (params = {}) => ({
        url: '/preferences/recommendations/',
        params,
      }),
      providesTags: ['Recommendations'],
    }),
    
    getUserAnalytics: builder.query({
      query: (timeframe = '30d') => `/preferences/analytics/?timeframe=${timeframe}`,
      providesTags: ['Analytics'],
    }),
  }),
});

export const {
  useSubmitOnboardingMutation,
  useGetUserPreferencesQuery,
  useUpdateUserPreferencesMutation,
  useLogInteractionMutation,
  useGetRecommendationsQuery,
  useGetUserAnalyticsQuery,
} = onboardingApi;

/**
 * Enhanced onboarding submission with validation and error handling
 */
export const submitOnboardingWithValidation = async (formData, dispatch) => {
  try {
    // Validate form data before submission
    const validation = validateOnboardingData(formData);
    
    if (!validation.isValid) {
      throw new Error(`Validation failed: ${Object.values(validation.errors).join(', ')}`);
    }

    // Transform form data to match backend schema
    const transformedData = transformOnboardingData(formData);
    
    // Submit to backend
    const result = await dispatch(
      onboardingApi.endpoints.submitOnboarding.initiate(transformedData)
    ).unwrap();

    // Log successful onboarding completion
    await dispatch(
      onboardingApi.endpoints.logInteraction.initiate({
        type: 'onboarding_completed',
        data: {
          completion_score: calculateCompletionScore(formData),
          total_steps: 6,
          time_taken: Date.now() - (formData._startTime || Date.now())
        },
        context: {
          user_agent: navigator.userAgent,
          screen_resolution: `${screen.width}x${screen.height}`,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        }
      })
    );

    return result;
  } catch (error) {
    console.error('Onboarding submission failed:', error);
    throw error;
  }
};

/**
 * Transform frontend form data to backend schema format
 */
const transformOnboardingData = (formData) => {
  return {
    basic_info: {
      learning_goals: formData.learning_goals || [],
      experience_level: formData.experience_level || '',
      preferred_pace: formData.preferred_pace || '',
      time_availability: formData.time_availability || '',
      learning_style: formData.learning_style || [],
      career_stage: formData.career_stage || '',
      target_timeline: formData.target_timeline || '',
    },
    content_preferences: {
      preferred_platforms: formData.preferred_platforms || [],
      content_types: formData.content_types || [],
      language_preference: formData.language_preference || ['english'],
      difficulty_preference: getDifficultyPreference(formData.experience_level),
      duration_preference: getDurationPreference(formData.time_availability),
    },
    initial_interaction: {
      type: 'onboarding_completed',
      data: {
        form_data: formData,
        completion_date: new Date().toISOString(),
        user_agent: navigator.userAgent,
      },
      context: {
        source: 'onboarding_flow',
        version: '1.0.0',
      }
    }
  };
};

/**
 * Helper function to determine difficulty preference from experience level
 */
const getDifficultyPreference = (experienceLevel) => {
  switch (experienceLevel) {
    case 'complete_beginner':
      return 'beginner';
    case 'some_basics':
      return 'mixed';
    case 'intermediate':
      return 'intermediate';
    case 'advanced':
      return 'advanced';
    default:
      return 'mixed';
  }
};

/**
 * Helper function to determine duration preference from time availability
 */
const getDurationPreference = (timeAvailability) => {
  switch (timeAvailability) {
    case '1-2hrs':
      return 'short';
    case '3-5hrs':
      return 'medium';
    case '5+hrs':
      return 'long';
    default:
      return 'mixed';
  }
};

/**
 * Track user interaction during onboarding
 */
export const trackOnboardingInteraction = (dispatch, interactionType, data = {}) => {
  try {
    dispatch(
      onboardingApi.endpoints.logInteraction.initiate({
        type: interactionType,
        data,
        context: {
          page: 'onboarding',
          timestamp: new Date().toISOString(),
          user_agent: navigator.userAgent,
        }
      })
    );
  } catch (error) {
    console.warn('Failed to track interaction:', error);
  }
};

// Import validation function from helpers
import { validateOnboardingData, calculateCompletionScore } from '@/utils/onboardingHelpers';