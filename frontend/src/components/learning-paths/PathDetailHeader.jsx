// File: frontend/src/components/learning-paths/PathDetailHeader.jsx
// Description: Header component for learning path detail page
// Why: Displays path metadata, progress, and status in a visually appealing header
// Relevant Files: app/learning-paths/[pathId]/page.jsx, ProgressBar.jsx

'use client';

import { Clock, Target, BookOpen, CheckCircle2, TrendingUp } from 'lucide-react';
import ProgressBar from './ProgressBar';

export default function PathDetailHeader({
  title,
  description,
  difficulty,
  duration,
  progress = 0,
  status = 'not_started',
  isCompleted = false
}) {
  const getDifficultyColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'beginner':
        return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300';
      case 'intermediate':
        return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300';
      case 'advanced':
        return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300';
    }
  };

  const getStatusInfo = () => {
    if (isCompleted || status === 'completed') {
      return {
        icon: CheckCircle2,
        text: 'Completed',
        color: 'text-green-600 dark:text-green-400',
        bgColor: 'bg-green-50 dark:bg-green-900/20'
      };
    }
    if (status === 'in_progress') {
      return {
        icon: TrendingUp,
        text: 'In Progress',
        color: 'text-blue-600 dark:text-blue-400',
        bgColor: 'bg-blue-50 dark:bg-blue-900/20'
      };
    }
    return {
      icon: BookOpen,
      text: 'Not Started',
      color: 'text-gray-600 dark:text-gray-400',
      bgColor: 'bg-gray-50 dark:bg-gray-800'
    };
  };

  const statusInfo = getStatusInfo();
  const StatusIcon = statusInfo.icon;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
      {/* Status Banner */}
      {isCompleted && (
        <div className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-6 py-3">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5" />
            <span className="font-semibold">Congratulations! You've completed this learning path!</span>
          </div>
        </div>
      )}

      <div className="p-6 md:p-8">
        {/* Title and Status */}
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-4">
          <div className="flex-1">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">
              {title}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 text-lg leading-relaxed">
              {description}
            </p>
          </div>

          <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${statusInfo.bgColor} flex-shrink-0`}>
            <StatusIcon className={`w-5 h-5 ${statusInfo.color}`} />
            <span className={`font-semibold ${statusInfo.color}`}>
              {statusInfo.text}
            </span>
          </div>
        </div>

        {/* Metadata */}
        <div className="flex flex-wrap items-center gap-6 mb-6">
          <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
            <Clock className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            <span className="font-medium">
              {duration === 1 ? 'Duration varies' : `${duration} hours`}
            </span>
          </div>

          <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium capitalize ${getDifficultyColor(difficulty)}`}>
            <Target className="w-4 h-4" />
            {difficulty}
          </div>

          <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
            <BookOpen className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            <span className="font-medium">AI-Generated</span>
          </div>
        </div>

        {/* Progress Section */}
        {status !== 'not_started' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Overall Progress
              </span>
              <span className="text-lg font-bold text-gray-900 dark:text-white">
                {Math.round(progress)}%
              </span>
            </div>
            <ProgressBar progress={progress} height="h-3" />
            {progress > 0 && progress < 100 && (
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Keep going! You're {Math.round(progress)}% through your learning journey.
              </p>
            )}
          </div>
        )}

        {/* Start Message */}
        {status === 'not_started' && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <p className="text-blue-900 dark:text-blue-200 font-medium">
              Ready to begin? Click "Start Learning" to begin your journey!
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
