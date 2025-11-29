// File: frontend/src/components/learning-paths/LessonCard.jsx
// Description: Individual lesson card with progress tracking
// Why: Displays lesson details and allows marking progress
// Relevant Files: ModulesList.jsx, store/api/learningPathsApi.js

'use client';

import { useState } from 'react';
import { useUpdateProgressMutation } from '@/store/api/learningPathsApi';
import {
  PlayCircle,
  CheckCircle,
  Clock,
  ExternalLink,
  Video,
  FileText,
  Code,
  HelpCircle,
  Trophy,
  Loader2
} from 'lucide-react';
import ProgressBar from './ProgressBar';

export default function LessonCard({ lesson, pathId, moduleId, lessonIndex, canStart }) {
  const [updateProgress, { isLoading }] = useUpdateProgressMutation();
  const [localProgress, setLocalProgress] = useState(lesson.progress_percentage || 0);

  const isCompleted = lesson.completed || localProgress === 100;

  const getLessonIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'video':
        return Video;
      case 'article':
      case 'reading':
        return FileText;
      case 'exercise':
      case 'interactive':
        return Code;
      case 'quiz':
        return HelpCircle;
      case 'project':
        return Trophy;
      default:
        return PlayCircle;
    }
  };

  const LessonIcon = getLessonIcon(lesson.type);

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
        : 'border-gray-200 dark:border-gray-700'
    } ${!canStart ? 'opacity-50' : 'hover:shadow-md'}`}>
      {/* Thumbnail Image */}
      {lesson.thumbnail && (
        <div className="w-full h-40 bg-gray-200 dark:bg-gray-700 overflow-hidden">
          <img
            src={lesson.thumbnail}
            alt={lesson.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = 'https://via.placeholder.com/320x180/6B7280/FFFFFF?text=Course';
            }}
          />
        </div>
      )}

      <div className="p-4">
        {/* Lesson Header */}
        <div className="flex items-start gap-3 mb-3">
          {/* Icon */}
          <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
            isCompleted
              ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
              : 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
          }`}>
            {isCompleted ? (
              <CheckCircle className="w-5 h-5" />
            ) : (
              <LessonIcon className="w-5 h-5" />
            )}
          </div>

          {/* Lesson Info */}
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
              {lesson.title}
            </h4>

            <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
              <span className="flex items-center gap-1 capitalize">
                <LessonIcon className="w-4 h-4" />
                {lesson.type}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {lesson.duration_minutes} min
              </span>
              <span className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded-full">
                {lesson.platform}
              </span>
            </div>

            {lesson.description && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 line-clamp-2">
                {lesson.description}
              </p>
            )}
          </div>
        </div>

        {/* Progress */}
        {canStart && !isCompleted && (
          <div className="mb-3">
            <ProgressBar progress={localProgress} height="h-2" />
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2">
          {lesson.url && (
            <a
              href={lesson.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium flex-1 justify-center"
            >
              <ExternalLink className="w-4 h-4" />
              {isCompleted ? 'Review' : 'Start Lesson'}
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
