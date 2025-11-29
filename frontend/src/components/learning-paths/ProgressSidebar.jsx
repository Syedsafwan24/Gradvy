// File: frontend/src/components/learning-paths/ProgressSidebar.jsx
// Description: Sidebar showing progress stats and analytics
// Why: Displays key metrics, next lesson, and analytics insights
// Relevant Files: app/learning-paths/[pathId]/page.jsx

'use client';

import {
  TrendingUp,
  Clock,
  Target,
  Calendar,
  Zap,
  BookOpen,
  CheckCircle2,
  AlertCircle,
  Loader2
} from 'lucide-react';
import ProgressBar from './ProgressBar';

export default function ProgressSidebar({
  pathData,
  analyticsData,
  showAnalytics,
  analyticsLoading
}) {
  if (!pathData) return null;

  const progress = pathData.progress_percentage || 0;
  const status = pathData.status;
  const modules = pathData.modules || [];

  // Calculate totals
  const totalModules = modules.length;
  const completedModules = modules.filter(
    (m) => (m.progress_percentage || 0) === 100
  ).length;

  const totalLessons = modules.reduce(
    (sum, m) => sum + (m.lessons?.length || 0),
    0
  );
  const completedLessons = modules.reduce(
    (sum, m) => sum + (m.completed_lessons || 0),
    0
  );

  // Find next lesson
  const getNextLesson = () => {
    for (const module of modules) {
      if (module.skipped) continue;
      for (const lesson of module.lessons || []) {
        if (!lesson.completed && (lesson.progress_percentage || 0) < 100) {
          return {
            moduleTitle: module.title,
            lessonTitle: lesson.title,
            lessonType: lesson.type,
            duration: lesson.duration_minutes
          };
        }
      }
    }
    return null;
  };

  const nextLesson = getNextLesson();

  return (
    <div className="space-y-6">
      {/* Progress Overview */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Target className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          Progress Overview
        </h3>

        <div className="space-y-4">
          {/* Overall Progress */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Overall</span>
              <span className="text-lg font-bold text-gray-900 dark:text-white">
                {Math.round(progress)}%
              </span>
            </div>
            <ProgressBar progress={progress} height="h-3" />
          </div>

          {/* Modules Progress */}
          <div className="flex items-center justify-between py-3 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
              <BookOpen className="w-4 h-4" />
              <span className="text-sm">Modules</span>
            </div>
            <span className="font-semibold text-gray-900 dark:text-white">
              {completedModules}/{totalModules}
            </span>
          </div>

          {/* Lessons Progress */}
          <div className="flex items-center justify-between pb-3 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
              <CheckCircle2 className="w-4 h-4" />
              <span className="text-sm">Lessons</span>
            </div>
            <span className="font-semibold text-gray-900 dark:text-white">
              {completedLessons}/{totalLessons}
            </span>
          </div>

          {/* Time Estimate */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
              <Clock className="w-4 h-4" />
              <span className="text-sm">Est. Time Left</span>
            </div>
            <span className="font-semibold text-gray-900 dark:text-white">
              {Math.round(pathData.estimated_duration_hours * (1 - progress / 100))}h
            </span>
          </div>
        </div>
      </div>

      {/* Next Lesson */}
      {status !== 'not_started' && nextLesson && (
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl shadow-lg p-6 border border-blue-200 dark:border-blue-800">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <Zap className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            Up Next
          </h3>

          <div className="space-y-2">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {nextLesson.moduleTitle}
            </p>
            <p className="font-semibold text-gray-900 dark:text-white">
              {nextLesson.lessonTitle}
            </p>
            <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400 pt-2">
              <span className="capitalize">{nextLesson.lessonType}</span>
              <span>•</span>
              <span>{nextLesson.duration} min</span>
            </div>
          </div>
        </div>
      )}

      {/* Analytics Section */}
      {showAnalytics && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            Analytics
          </h3>

          {analyticsLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
            </div>
          ) : analyticsData ? (
            <div className="space-y-4">
              {/* Learning Velocity */}
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Learning Velocity
                  </span>
                </div>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {analyticsData.learning_velocity?.toFixed(1) || 0}
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  lessons per week
                </p>
              </div>

              {/* Estimated Completion */}
              {analyticsData.estimated_completion_date && (
                <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar className="w-4 h-4 text-green-600 dark:text-green-400" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Est. Completion
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-green-600 dark:text-green-400">
                    {new Date(analyticsData.estimated_completion_date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </p>
                </div>
              )}

              {/* Struggle Areas */}
              {analyticsData.struggle_areas && analyticsData.struggle_areas.length > 0 && (
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Needs Focus
                    </span>
                  </div>
                  <ul className="space-y-1 text-xs text-gray-600 dark:text-gray-400">
                    {analyticsData.struggle_areas.slice(0, 3).map((area, index) => (
                      <li key={index} className="truncate">• {area.title || area.name}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommendations */}
              {analyticsData.recommendations && analyticsData.recommendations.length > 0 && (
                <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                    Recommendations
                  </h4>
                  <ul className="space-y-2">
                    {analyticsData.recommendations.slice(0, 3).map((rec, index) => (
                      <li
                        key={index}
                        className="text-xs text-gray-600 dark:text-gray-400 flex items-start gap-2"
                      >
                        <span className="text-blue-600 dark:text-blue-400">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
              Start learning to see analytics
            </p>
          )}
        </div>
      )}

      {/* Status Badge */}
      {pathData.started_at && (
        <div className="bg-gray-50 dark:bg-gray-750 rounded-xl shadow p-4 text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Started on</p>
          <p className="text-sm font-semibold text-gray-900 dark:text-white">
            {new Date(pathData.started_at).toLocaleDateString('en-US', {
              month: 'long',
              day: 'numeric',
              year: 'numeric'
            })}
          </p>
        </div>
      )}
    </div>
  );
}
