// File: frontend/src/components/learning-paths/ProgressBar.jsx
// Description: Reusable progress bar component
// Why: Visual indicator for progress tracking across the app
// Relevant Files: PathDetailHeader.jsx, ModulesList.jsx, LessonCard.jsx

'use client';

export default function ProgressBar({ progress = 0, height = 'h-2', showLabel = false, className = '' }) {
  const clampedProgress = Math.min(Math.max(progress, 0), 100);

  const getColorClass = () => {
    if (clampedProgress === 100) {
      return 'bg-gradient-to-r from-green-500 to-emerald-500';
    }
    if (clampedProgress >= 75) {
      return 'bg-gradient-to-r from-blue-500 to-cyan-500';
    }
    if (clampedProgress >= 50) {
      return 'bg-gradient-to-r from-blue-500 to-indigo-500';
    }
    if (clampedProgress >= 25) {
      return 'bg-gradient-to-r from-indigo-500 to-purple-500';
    }
    return 'bg-gradient-to-r from-gray-400 to-gray-500';
  };

  return (
    <div className={className}>
      {showLabel && (
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Progress
          </span>
          <span className="text-sm font-bold text-gray-900 dark:text-white">
            {Math.round(clampedProgress)}%
          </span>
        </div>
      )}
      <div className={`w-full ${height} bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden`}>
        <div
          className={`${height} ${getColorClass()} transition-all duration-500 ease-out rounded-full`}
          style={{ width: `${clampedProgress}%` }}
          role="progressbar"
          aria-valuenow={clampedProgress}
          aria-valuemin="0"
          aria-valuemax="100"
        />
      </div>
    </div>
  );
}
