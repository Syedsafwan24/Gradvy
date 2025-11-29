// File: frontend/src/components/learning-paths/lesson-cards/ArticleLessonCard.jsx
// Description: Specialized card for article lessons with reading-optimized UI
// Why: Provides article-specific visual design (icon-based, blue theme, read button)
// Relevant Files: LessonCard.jsx, VideoLessonCard.jsx, ProgressBar.jsx

'use client';

import { useState } from 'react';
import { useUpdateProgressMutation } from '@/store/api/learningPathsApi';
import {
  FileText,
  CheckCircle,
  Clock,
  ExternalLink,
  BookOpen,
  Loader2
} from 'lucide-react';
import ProgressBar from '../ProgressBar';

export default function ArticleLessonCard({ lesson, pathId, moduleId, lessonIndex, canStart }) {
  const [updateProgress, { isLoading }] = useUpdateProgressMutation();
  const [localProgress, setLocalProgress] = useState(lesson.progress_percentage || 0);

  const isCompleted = lesson.completed || localProgress === 100;

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
        : 'border-blue-200 dark:border-blue-800'
    } ${!canStart ? 'opacity-50' : 'hover:shadow-lg hover:border-blue-300'}`}>
      {/* Article Header - Icon-based instead of thumbnail */}
      <div className={`w-full h-24 flex items-center justify-center ${
        isCompleted
          ? 'bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20'
          : 'bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20'
      }`}>
        <div className={`rounded-full p-5 ${
          isCompleted
            ? 'bg-green-100 dark:bg-green-900/30'
            : 'bg-blue-100 dark:bg-blue-900/30'
        }`}>
          {isCompleted ? (
            <CheckCircle className="w-12 h-12 text-green-600 dark:text-green-400" />
          ) : (
            <FileText className="w-12 h-12 text-blue-600 dark:text-blue-400" />
          )}
        </div>

        {/* Platform badge */}
        {lesson.platform && (
          <div className="absolute top-3 right-3 bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-medium">
            {lesson.platform}
          </div>
        )}
      </div>

      <div className="p-4">
        {/* Lesson Header */}
        <div className="mb-3">
          <h4 className="font-semibold text-gray-900 dark:text-white mb-2 text-lg">
            {lesson.title}
          </h4>

          <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1">
              <BookOpen className="w-4 h-4 text-blue-500" />
              Article
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {lesson.duration_minutes > 0 ? `${lesson.duration_minutes} min read` : 'Quick read'}
            </span>
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
            <ProgressBar progress={localProgress} height="h-2" color="blue" />
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
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
            >
              {isCompleted ? (
                <>
                  <ExternalLink className="w-4 h-4" />
                  Read Again
                </>
              ) : (
                <>
                  <BookOpen className="w-4 h-4" />
                  Read Article
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
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
          </div>
        )}
      </div>
    </div>
  );
}
