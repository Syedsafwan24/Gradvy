// File: frontend/src/components/learning-paths/LearningPathsList.jsx
// Description: Displays list of learning paths with cards and filtering
// Why: Shows user's learning paths in a clean, organized card layout with status filtering
// Relevant Files: app/learning-paths/page.jsx, LearningPathCard.jsx

'use client';

import { BookOpen, Clock, TrendingUp, CheckCircle, PlayCircle, Loader2 } from 'lucide-react';

export default function LearningPathsList({ data, isLoading, error, view, onViewPath }) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-3" />
          <p className="text-gray-600 dark:text-gray-400">Loading learning paths...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
        <h3 className="text-red-900 dark:text-red-200 font-semibold mb-2">
          Failed to load learning paths
        </h3>
        <p className="text-red-700 dark:text-red-300 text-sm">
          {error?.data?.error?.message || 'Please try again later'}
        </p>
      </div>
    );
  }

  // Filter paths based on view
  const filteredPaths = data?.active_paths?.filter((path) => {
    if (view === 'active') return path.status === 'in_progress';
    if (view === 'completed') return path.status === 'completed';
    return true; // 'all' view
  }) || [];

  if (filteredPaths.length === 0) {
    return (
      <div className="text-center py-12">
        <BookOpen className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          No {view !== 'all' ? view : ''} learning paths yet
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Generate your first AI-powered learning path to get started
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {filteredPaths.map((path) => (
        <LearningPathCard
          key={path.path_id}
          path={path}
          onClick={() => onViewPath(path.path_id)}
        />
      ))}
    </div>
  );
}

function LearningPathCard({ path, onClick }) {
  const getStatusBadge = (status) => {
    switch (status) {
      case 'not_started':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs font-medium rounded-full">
            <PlayCircle className="w-3 h-3" />
            Not Started
          </span>
        );
      case 'in_progress':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-medium rounded-full">
            <TrendingUp className="w-3 h-3" />
            In Progress
          </span>
        );
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs font-medium rounded-full">
            <CheckCircle className="w-3 h-3" />
            Completed
          </span>
        );
      default:
        return null;
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner':
        return 'text-green-600 dark:text-green-400';
      case 'intermediate':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'advanced':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  const progress = path.progress_percentage || 0;

  return (
    <div
      onClick={onClick}
      className="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-xl transition-shadow cursor-pointer border border-gray-200 dark:border-gray-700 overflow-hidden group"
    >
      {/* Progress Bar */}
      <div className="h-2 bg-gray-200 dark:bg-gray-700">
        <div
          className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-2">
            {path.title}
          </h3>
          {getStatusBadge(path.status)}
        </div>

        {/* Description */}
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
          {path.description}
        </p>

        {/* Metadata */}
        <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-4">
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            <span>{path.estimated_duration_hours}h</span>
          </div>
          <div className={`font-medium capitalize ${getDifficultyColor(path.difficulty_level)}`}>
            {path.difficulty_level}
          </div>
        </div>

        {/* Progress */}
        {path.status !== 'not_started' && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Progress</span>
            <span className="font-semibold text-gray-900 dark:text-white">
              {Math.round(progress)}%
            </span>
          </div>
        )}

        {/* Modules Info */}
        {path.modules && path.modules.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
              <span>{path.modules.length} modules</span>
              {path.status === 'not_started' && (
                <span className="text-blue-600 dark:text-blue-400 font-medium">
                  Start learning →
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
