// File: frontend/src/components/learning-paths/lesson-cards/ProjectLessonCard.jsx
// Description: Specialized card for project/tutorial lessons with project-optimized UI
// Why: Provides project-specific visual design (purple gradient, GitHub stars, hands-on focus)
// Relevant Files: LessonCard.jsx, VideoLessonCard.jsx, ProgressBar.jsx

'use client';

import { useState } from 'react';
import { useUpdateProgressMutation } from '@/store/api/learningPathsApi';
import {
  Trophy,
  CheckCircle,
  Clock,
  ExternalLink,
  Github,
  Loader2,
  Star,
  Folder
} from 'lucide-react';
import ProgressBar from '../ProgressBar';

export default function ProjectLessonCard({ lesson, pathId, moduleId, lessonIndex, canStart }) {
  const [updateProgress, { isLoading }] = useUpdateProgressMutation();
  const [localProgress, setLocalProgress] = useState(lesson.progress_percentage || 0);

  const isCompleted = lesson.completed || localProgress === 100;

  // Extract GitHub stars if available (from course metadata)
  const getStarsCount = () => {
    if (lesson.stars || lesson.github_stars) {
      const stars = lesson.stars || lesson.github_stars;
      if (stars >= 1000) {
        return `${(stars / 1000).toFixed(1)}k`;
      }
      return stars.toString();
    }
    return null;
  };

  const starsCount = getStarsCount();

  const handleMarkComplete = async () => {
    if (!canStart) return;

    try {
      await updateProgress({
        pathId,
        module_id: moduleId,
        lesson_id: lesson.lesson_id,
        progress_percentage: 100,
        completed: true,
        time_spent_minutes: lesson.duration_minutes || 0,
      }).unwrap();

      setLocalProgress(100);
    } catch (error) {
      console.error('Failed to update progress:', error);
    }
  };

  const handleUpdateProgress = async (newProgress) => {
    if (!canStart) return;

    try {
      setLocalProgress(newProgress);

      await updateProgress({
        pathId,
        module_id: moduleId,
        lesson_id: lesson.lesson_id,
        progress_percentage: newProgress,
        completed: newProgress === 100,
        time_spent_minutes: Math.round((lesson.duration_minutes || 0) * (newProgress / 100)),
      }).unwrap();
    } catch (error) {
      console.error('Failed to update progress:', error);
    }
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg border-2 transition-all overflow-hidden ${
      isCompleted
        ? 'border-green-500 dark:border-green-400'
        : 'border-purple-200 dark:border-purple-800'
    } ${!canStart ? 'opacity-50' : 'hover:shadow-lg hover:border-purple-300'}`}>
      {/* Project Header - Purple Gradient */}
      <div className={`w-full h-32 flex items-center justify-center relative ${
        isCompleted
          ? 'bg-gradient-to-br from-green-50 via-green-100 to-emerald-100 dark:from-green-900/20 dark:via-green-800/20 dark:to-emerald-800/20'
          : 'bg-gradient-to-br from-purple-50 via-purple-100 to-pink-100 dark:from-purple-900/20 dark:via-purple-800/20 dark:to-pink-800/20'
      }`}>
        <div className={`rounded-lg p-4 ${
          isCompleted
            ? 'bg-green-100 dark:bg-green-900/30'
            : 'bg-purple-100 dark:bg-purple-900/30'
        }`}>
          {isCompleted ? (
            <CheckCircle className="w-12 h-12 text-green-600 dark:text-green-400" />
          ) : (
            <Trophy className="w-12 h-12 text-purple-600 dark:text-purple-400" />
          )}
        </div>

        {/* GitHub stars badge (if available) */}
        {starsCount && (
          <div className="absolute top-3 right-3 bg-yellow-500 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
            <Star className="w-3 h-3 fill-white" />
            {starsCount}
          </div>
        )}

        {/* Project type badge */}
        <div className="absolute top-3 left-3 bg-purple-600 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1">
          {lesson.platform === 'github' ? (
            <>
              <Github className="w-3 h-3" />
              GitHub
            </>
          ) : (
            <>
              <Folder className="w-3 h-3" />
              Project
            </>
          )}
        </div>
      </div>

      <div className="p-4">
        {/* Lesson Header */}
        <div className="mb-3">
          <h4 className="font-semibold text-gray-900 dark:text-white mb-2 text-lg">
            {lesson.title}
          </h4>

          <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1">
              <Trophy className="w-4 h-4 text-purple-500" />
              Hands-on Project
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {lesson.duration_minutes > 0 ? `~${lesson.duration_minutes} min` : 'Self-paced'}
            </span>
            {lesson.language && (
              <span className="text-xs px-2 py-0.5 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded-full font-medium">
                {lesson.language}
              </span>
            )}
          </div>

          {lesson.description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-3 line-clamp-3">
              {lesson.description}
            </p>
          )}
        </div>

        {/* Progress */}
        {canStart && !isCompleted && (
          <div className="mb-3">
            <ProgressBar progress={localProgress} height="h-2" color="purple" />
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2">
          {lesson.url && (
            <a
              href={lesson.url}
              target="_blank"
              rel="noopener noreferrer"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors text-sm font-medium flex-1 justify-center ${
                isCompleted
                  ? 'bg-gray-600 hover:bg-gray-700 text-white'
                  : 'bg-purple-600 hover:bg-purple-700 text-white'
              }`}
            >
              {isCompleted ? (
                <>
                  <ExternalLink className="w-4 h-4" />
                  View Again
                </>
              ) : (
                <>
                  {lesson.platform === 'github' ? (
                    <Github className="w-4 h-4" />
                  ) : (
                    <Folder className="w-4 h-4" />
                  )}
                  View Project
                </>
              )}
            </a>
          )}

          {canStart && !isCompleted && (
            <button
              onClick={handleMarkComplete}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium disabled:opacity-50"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <CheckCircle className="w-4 h-4" />
              )}
              Complete
            </button>
          )}

          {isCompleted && (
            <div className="flex items-center gap-2 text-green-600 dark:text-green-400 text-sm font-medium">
              <CheckCircle className="w-4 h-4" />
              Completed
            </div>
          )}
        </div>

        {/* Progress Slider (if in progress) */}
        {canStart && localProgress > 0 && localProgress < 100 && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <label className="block text-xs text-gray-600 dark:text-gray-400 mb-2">
              Update Progress: {Math.round(localProgress)}%
            </label>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={localProgress}
              onChange={(e) => handleUpdateProgress(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-600"
            />
          </div>
        )}
      </div>
    </div>
  );
}
