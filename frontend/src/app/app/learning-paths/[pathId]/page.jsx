// File: frontend/src/app/learning-paths/[pathId]/page.jsx
// Description: Learning path detail page showing modules, lessons, and progress
// Why: Displays full learning path structure with progress tracking and navigation through lessons
// Relevant Files: components/learning-paths/PathDetail.jsx, store/api/learningPathsApi.js

'use client';

import { use } from 'react';
import { useRouter } from 'next/navigation';
import {
  useGetLearningPathDetailQuery,
  useStartLearningPathMutation,
  useGetProgressAnalyticsQuery
} from '@/store/api/learningPathsApi';
import PathDetailHeader from '@/components/learning-paths/PathDetailHeader';
import ModulesList from '@/components/learning-paths/ModulesList';
import ProgressSidebar from '@/components/learning-paths/ProgressSidebar';
import { ArrowLeft, PlayCircle, BarChart3 } from 'lucide-react';
import { useState } from 'react';

export default function LearningPathDetailPage({ params }) {
  const unwrappedParams = use(params);
  const pathId = unwrappedParams.pathId;
  const router = useRouter();

  const [showAnalytics, setShowAnalytics] = useState(false);

  const {
    data: pathData,
    isLoading,
    error
  } = useGetLearningPathDetailQuery(pathId);

  const {
    data: analyticsData,
    isLoading: analyticsLoading
  } = useGetProgressAnalyticsQuery(pathId, {
    skip: !showAnalytics
  });

  const [startPath, { isLoading: isStarting }] = useStartLearningPathMutation();

  const handleBack = () => {
    router.push('/app/learning-paths');
  };

  const handleStartPath = async () => {
    try {
      await startPath(pathId).unwrap();
    } catch (err) {
      console.error('Failed to start learning path:', err);
    }
  };

  const handleToggleAnalytics = () => {
    setShowAnalytics(!showAnalytics);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading learning path...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center max-w-md">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Error Loading Path
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {error?.data?.error?.message || 'Failed to load learning path'}
          </p>
          <button
            onClick={handleBack}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Back to Learning Paths
          </button>
        </div>
      </div>
    );
  }

  const isNotStarted = pathData?.status === 'not_started';
  const isCompleted = pathData?.status === 'completed';

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header Bar */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 max-w-7xl">
          <div className="flex items-center justify-between">
            <button
              onClick={handleBack}
              className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Back
            </button>

            <div className="flex items-center gap-3">
              {isNotStarted && (
                <button
                  onClick={handleStartPath}
                  disabled={isStarting}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  <PlayCircle className="w-5 h-5" />
                  {isStarting ? 'Starting...' : 'Start Learning'}
                </button>
              )}

              <button
                onClick={handleToggleAnalytics}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  showAnalytics
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                }`}
              >
                <BarChart3 className="w-5 h-5" />
                Analytics
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Column - Path Details */}
          <div className="lg:col-span-2 space-y-6">
            <PathDetailHeader
              title={pathData?.title}
              description={pathData?.description}
              difficulty={pathData?.difficulty_level}
              duration={pathData?.estimated_duration_hours}
              progress={pathData?.progress_percentage}
              status={pathData?.status}
              isCompleted={isCompleted}
            />

            <ModulesList
              modules={pathData?.modules || []}
              pathId={pathId}
              status={pathData?.status}
            />
          </div>

          {/* Sidebar - Progress & Analytics */}
          <div className="lg:col-span-1">
            <ProgressSidebar
              pathData={pathData}
              analyticsData={analyticsData}
              showAnalytics={showAnalytics}
              analyticsLoading={analyticsLoading}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
