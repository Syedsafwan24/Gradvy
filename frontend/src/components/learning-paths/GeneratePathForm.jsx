// File: frontend/src/components/learning-paths/GeneratePathForm.jsx
// Description: Form component for generating personalized learning paths
// Why: Collects user preferences and submits to AI-powered path generation endpoint
// Relevant Files: store/api/learningPathsApi.js, app/learning-paths/generate/page.jsx

'use client';

import { useState, useMemo, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useGenerateLearningPathMutation } from '@/store/api/learningPathsApi';
import { useGetUserPreferencesQuery } from '@/services/preferencesApi';
import { Loader2, Sparkles, AlertCircle, CheckCircle2 } from 'lucide-react';

const LEARNING_GOALS_OPTIONS = [
  { value: 'web_dev', label: 'Web Development' },
  { value: 'mobile_dev', label: 'Mobile Development' },
  { value: 'ai_ml', label: 'AI & Machine Learning' },
  { value: 'data_science', label: 'Data Science' },
  { value: 'devops', label: 'DevOps & Cloud' },
  { value: 'cybersecurity', label: 'Cybersecurity' },
  { value: 'blockchain', label: 'Blockchain' },
  { value: 'game_dev', label: 'Game Development' },
];

const LEARNING_STYLES_OPTIONS = [
  { value: 'visual', label: 'Visual (diagrams, infographics)' },
  { value: 'hands_on', label: 'Hands-on (projects, exercises)' },
  { value: 'reading', label: 'Reading (articles, documentation)' },
  { value: 'videos', label: 'Videos (tutorials, courses)' },
  { value: 'interactive', label: 'Interactive (quizzes, coding challenges)' },
];

export default function GeneratePathForm({ onSuccess }) {
  // Fetch user preferences from the backend with automatic refetch on mount
  // This ensures fresh data after user updates preferences on another page
  const { data: userPreferences, isLoading: loadingPreferences, error: preferencesError } = useGetUserPreferencesQuery(undefined, {
    refetchOnMountOrArgChange: true
  });

  // Memoized default values from user preferences or fallback to hardcoded defaults
  const defaultFormValues = useMemo(() => {
    if (!userPreferences?.basic_info) {
      return {
        learning_goals: [],
        experience_level: 'intermediate',
        preferred_pace: 'medium',
        time_availability: '3-5hrs',
        learning_styles: ['hands_on', 'videos'],
        target_timeline: '6months',
        force_regenerate: false,
      };
    }

    const basicInfo = userPreferences.basic_info;
    return {
      learning_goals: basicInfo.learning_goals || [],
      experience_level: basicInfo.experience_level || 'intermediate',
      preferred_pace: basicInfo.preferred_pace || 'medium',
      time_availability: basicInfo.time_availability || '3-5hrs',
      learning_styles: basicInfo.learning_style || ['hands_on', 'videos'],
      target_timeline: basicInfo.target_timeline || '6months',
      force_regenerate: false,
    };
  }, [userPreferences]);

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: defaultFormValues,
  });

  const [generatePath, { isLoading, error }] = useGenerateLearningPathMutation();
  const [selectedGoals, setSelectedGoals] = useState(defaultFormValues.learning_goals);
  const [selectedStyles, setSelectedStyles] = useState(defaultFormValues.learning_styles);

  // Update form and state when preferences are loaded
  useEffect(() => {
    if (userPreferences?.basic_info) {
      reset(defaultFormValues);
      setSelectedGoals(defaultFormValues.learning_goals);
      setSelectedStyles(defaultFormValues.learning_styles);
    }
  }, [userPreferences, defaultFormValues, reset]);

  const toggleGoal = (goal) => {
    setSelectedGoals((prev) =>
      prev.includes(goal)
        ? prev.filter((g) => g !== goal)
        : [...prev, goal]
    );
  };

  const toggleStyle = (style) => {
    setSelectedStyles((prev) =>
      prev.includes(style)
        ? prev.filter((s) => s !== style)
        : [...prev, style]
    );
  };

  const onSubmit = async (data) => {
    try {
      const payload = {
        ...data,
        learning_goals: selectedGoals,
        learning_styles: selectedStyles,
      };

      const response = await generatePath(payload).unwrap();

      // Extract path_id from response
      const pathId = response?.path_id;
      if (pathId && onSuccess) {
        onSuccess(pathId);
      }
    } catch (err) {
      console.error('Failed to generate learning path:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
      {/* Loading Preferences Indicator */}
      {loadingPreferences && (
        <div className="flex items-center gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <Loader2 className="w-5 h-5 text-blue-600 dark:text-blue-400 animate-spin flex-shrink-0" />
          <p className="text-sm text-blue-900 dark:text-blue-200">
            Loading your saved preferences...
          </p>
        </div>
      )}

      {/* Using Saved Preferences Indicator */}
      {!loadingPreferences && userPreferences?.basic_info && (
        <div className="flex items-start gap-3 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-green-900 dark:text-green-200">
              Using your saved preferences
            </p>
            <p className="text-sm text-green-700 dark:text-green-300 mt-1">
              We've pre-filled the form with your previously saved learning preferences. Feel free to modify them if needed.
            </p>
          </div>
        </div>
      )}

      {/* Preferences Error Indicator */}
      {!loadingPreferences && preferencesError && (
        <div className="flex items-start gap-3 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
          <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-yellow-900 dark:text-yellow-200">
              Using default preferences
            </p>
            <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
              We couldn't load your saved preferences, so we're using defaults. Your selections will be saved when you generate a path.
            </p>
          </div>
        </div>
      )}

      {/* Learning Goals */}
      <div>
        <label className="block text-lg font-semibold text-gray-900 dark:text-white mb-3">
          What do you want to learn? *
        </label>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Select one or more learning goals
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {LEARNING_GOALS_OPTIONS.map((goal) => (
            <button
              key={goal.value}
              type="button"
              onClick={() => toggleGoal(goal.value)}
              className={`p-3 rounded-lg border-2 transition-all ${
                selectedGoals.includes(goal.value)
                  ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              {goal.label}
            </button>
          ))}
        </div>
        {selectedGoals.length === 0 && (
          <p className="text-sm text-red-600 dark:text-red-400 mt-2">
            Please select at least one learning goal
          </p>
        )}
      </div>

      {/* Experience Level */}
      <div>
        <label className="block text-lg font-semibold text-gray-900 dark:text-white mb-3">
          What's your experience level?
        </label>
        <select
          {...register('experience_level')}
          className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="complete_beginner">Complete Beginner</option>
          <option value="some_basics">Some Basics</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>

      {/* Learning Pace */}
      <div>
        <label className="block text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Preferred learning pace
        </label>
        <div className="grid grid-cols-3 gap-3">
          {['slow', 'medium', 'fast'].map((pace) => (
            <label
              key={pace}
              className={`flex items-center justify-center p-4 rounded-lg border-2 cursor-pointer transition-all ${
                watch('preferred_pace') === pace
                  ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              <input
                type="radio"
                {...register('preferred_pace')}
                value={pace}
                className="sr-only"
              />
              <span className="capitalize">{pace}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Time Availability */}
      <div>
        <label className="block text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Weekly time commitment
        </label>
        <select
          {...register('time_availability')}
          className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="1-2hrs">1-2 hours per week</option>
          <option value="3-5hrs">3-5 hours per week</option>
          <option value="5+hrs">5+ hours per week</option>
        </select>
      </div>

      {/* Learning Styles */}
      <div>
        <label className="block text-lg font-semibold text-gray-900 dark:text-white mb-3">
          How do you prefer to learn?
        </label>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Select your preferred content types
        </p>
        <div className="space-y-2">
          {LEARNING_STYLES_OPTIONS.map((style) => (
            <label
              key={style.value}
              className="flex items-center p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-750 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selectedStyles.includes(style.value)}
                onChange={() => toggleStyle(style.value)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="ml-3 text-gray-900 dark:text-white">{style.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Target Timeline */}
      <div>
        <label className="block text-lg font-semibold text-gray-900 dark:text-white mb-3">
          When do you want to complete this?
        </label>
        <select
          {...register('target_timeline')}
          className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="3months">3 months</option>
          <option value="6months">6 months</option>
          <option value="1year">1 year</option>
          <option value="flexible">Flexible / No deadline</option>
        </select>
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-900 dark:text-red-200">
              Failed to generate learning path
            </p>
            <p className="text-sm text-red-700 dark:text-red-300 mt-1">
              {error?.data?.error?.message || 'Please try again or contact support'}
            </p>
          </div>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading || selectedGoals.length === 0}
        className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Generating your personalized path...
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" />
            Generate Learning Path
          </>
        )}
      </button>

      <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
        This usually takes 10-30 seconds. Our AI is analyzing your preferences to create the perfect learning path for you.
      </p>
    </form>
  );
}
