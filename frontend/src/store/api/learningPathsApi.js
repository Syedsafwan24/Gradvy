// File: frontend/src/store/api/learningPathsApi.js
// Description: RTK Query API slice for learning path operations
// Why: Provides type-safe API endpoints for learning path generation, retrieval, progress tracking, and customization
// Relevant Files: store/api/apiSlice.js, components/learning-paths/, app/learning-paths/

import { apiSlice } from './apiSlice';

/**
 * Learning Paths API Slice
 *
 * Provides endpoints for:
 * - Generating personalized learning paths
 * - Retrieving learning paths (list and detail)
 * - Tracking progress through lessons
 * - Customizing learning paths
 * - Getting analytics and insights
 */
export const learningPathsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    /**
     * Generate a new personalized learning path
     * POST /api/learning-paths/generate/
     */
    generateLearningPath: builder.mutation({
      query: (data) => ({
        url: 'learning-paths/generate/',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['LearningPaths', 'MyLearningPaths'],
      transformResponse: (response) => response.data,
      transformErrorResponse: (response) => ({
        status: response.status,
        error: response.data?.error || response.error,
      }),
    }),

    /**
     * Get all learning paths for the authenticated user
     * GET /api/learning-paths/
     */
    getLearningPaths: builder.query({
      query: () => 'learning-paths/',
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ path_id }) => ({ type: 'LearningPaths', id: path_id })),
              { type: 'LearningPaths', id: 'LIST' },
            ]
          : [{ type: 'LearningPaths', id: 'LIST' }],
      transformResponse: (response) => response.data,
    }),

    /**
     * Get dashboard view of active learning paths
     * GET /api/learning-paths/my/
     */
    getMyLearningPaths: builder.query({
      query: () => 'learning-paths/my/',
      providesTags: ['MyLearningPaths'],
      transformResponse: (response) => response.data,
    }),

    /**
     * Get detailed information about a specific learning path
     * GET /api/learning-paths/{pathId}/
     */
    getLearningPathDetail: builder.query({
      query: (pathId) => `learning-paths/${pathId}/`,
      providesTags: (result, error, pathId) => [{ type: 'LearningPaths', id: pathId }],
      transformResponse: (response) => response.data,
    }),

    /**
     * Start a learning path (mark as in progress)
     * POST /api/learning-paths/{pathId}/start/
     */
    startLearningPath: builder.mutation({
      query: (pathId) => ({
        url: `learning-paths/${pathId}/start/`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, pathId) => [
        { type: 'LearningPaths', id: pathId },
        'MyLearningPaths',
      ],
      transformResponse: (response) => response.data,
    }),

    /**
     * Update progress for a lesson
     * PATCH /api/learning-paths/{pathId}/progress/
     */
    updateProgress: builder.mutation({
      query: ({ pathId, ...progressData }) => ({
        url: `learning-paths/${pathId}/progress/`,
        method: 'PATCH',
        body: {
          path_id: pathId,  // Backend expects path_id in body
          ...progressData,
        },
      }),
      invalidatesTags: (result, error, { pathId }) => [
        { type: 'LearningPaths', id: pathId },
        'MyLearningPaths',
        'Analytics',
      ],
      transformResponse: (response) => response.data,
      // Optimistic update for better UX
      async onQueryStarted({ pathId, ...progressData }, { dispatch, queryFulfilled }) {
        const patchResult = dispatch(
          learningPathsApi.util.updateQueryData('getLearningPathDetail', pathId, (draft) => {
            // Update progress optimistically
            if (draft && draft.modules) {
              for (const module of draft.modules) {
                for (const lesson of module.lessons || []) {
                  if (lesson.lesson_id === progressData.lesson_id) {
                    lesson.progress_percentage = progressData.progress_percentage;
                    lesson.completed = progressData.completed;
                    lesson.time_spent_minutes = progressData.time_spent_minutes;
                    break;
                  }
                }
              }
            }
          })
        );

        try {
          await queryFulfilled;
        } catch {
          patchResult.undo();
        }
      },
    }),

    /**
     * Customize a learning path
     * POST /api/learning-paths/{pathId}/customize/
     */
    customizeLearningPath: builder.mutation({
      query: ({ pathId, ...customizationData }) => ({
        url: `learning-paths/${pathId}/customize/`,
        method: 'POST',
        body: customizationData,
      }),
      invalidatesTags: (result, error, { pathId }) => [
        { type: 'LearningPaths', id: pathId },
      ],
      transformResponse: (response) => response.data,
    }),

    /**
     * Get progress analytics for a learning path
     * GET /api/learning-paths/{pathId}/analytics/
     */
    getProgressAnalytics: builder.query({
      query: (pathId) => `learning-paths/${pathId}/analytics/`,
      providesTags: (result, error, pathId) => [
        { type: 'Analytics', id: pathId },
      ],
      transformResponse: (response) => response.data,
    }),

    // ========================================================================
    // Quiz Endpoints
    // ========================================================================

    /**
     * Get or create quiz for a lesson
     * GET /api/learning-paths/quizzes/{pathId}/{lessonId}/
     */
    getQuiz: builder.query({
      query: ({ pathId, lessonId }) => `learning-paths/quizzes/${pathId}/${lessonId}/`,
      providesTags: (result, error, { pathId, lessonId }) => [
        { type: 'Quiz', id: `${pathId}-${lessonId}` },
      ],
      transformResponse: (response) => response.data,
    }),

    /**
     * Start a quiz attempt
     * POST /api/learning-paths/quizzes/{quizId}/start/
     */
    startQuizAttempt: builder.mutation({
      query: (quizId) => ({
        url: `learning-paths/quizzes/${quizId}/start/`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, quizId) => [
        { type: 'QuizAttempts', id: quizId },
      ],
      transformResponse: (response) => response.data,
    }),

    /**
     * Submit quiz answers
     * POST /api/learning-paths/quizzes/attempts/{attemptId}/submit/
     */
    submitQuiz: builder.mutation({
      query: ({ attemptId, answers }) => ({
        url: `learning-paths/quizzes/attempts/${attemptId}/submit/`,
        method: 'POST',
        body: {
          attempt_id: attemptId,
          answers,
        },
      }),
      invalidatesTags: (result, error, { attemptId }) => [
        { type: 'QuizAttempt', id: attemptId },
        'LearningPaths', // Invalidate paths to refresh lock states
      ],
      transformResponse: (response) => response.data,
    }),

    /**
     * Get quiz attempt results
     * GET /api/learning-paths/quizzes/attempts/{attemptId}/
     */
    getQuizAttempt: builder.query({
      query: (attemptId) => `learning-paths/quizzes/attempts/${attemptId}/`,
      providesTags: (result, error, attemptId) => [
        { type: 'QuizAttempt', id: attemptId },
      ],
      transformResponse: (response) => response.data,
    }),

    /**
     * Get all quiz attempts for a lesson
     * GET /api/learning-paths/quizzes/{pathId}/{lessonId}/attempts/
     */
    getQuizAttempts: builder.query({
      query: ({ pathId, lessonId }) => `learning-paths/quizzes/${pathId}/${lessonId}/attempts/`,
      providesTags: (result, error, { pathId, lessonId }) => [
        { type: 'QuizAttempts', id: `${pathId}-${lessonId}` },
      ],
      transformResponse: (response) => response.data,
    }),
  }),
});

// Export hooks for usage in components
export const {
  useGenerateLearningPathMutation,
  useGetLearningPathsQuery,
  useGetMyLearningPathsQuery,
  useGetLearningPathDetailQuery,
  useStartLearningPathMutation,
  useUpdateProgressMutation,
  useCustomizeLearningPathMutation,
  useGetProgressAnalyticsQuery,
  // Quiz hooks
  useGetQuizQuery,
  useStartQuizAttemptMutation,
  useSubmitQuizMutation,
  useGetQuizAttemptQuery,
  useGetQuizAttemptsQuery,
  // Lazy query hooks
  useLazyGetLearningPathsQuery,
  useLazyGetLearningPathDetailQuery,
  useLazyGetProgressAnalyticsQuery,
  useLazyGetQuizQuery,
  useLazyGetQuizAttemptQuery,
  useLazyGetQuizAttemptsQuery,
} = learningPathsApi;

// Export the API slice for store configuration
export default learningPathsApi;
