// File: frontend/src/app/learning-paths/page.jsx
// Description: Main learning paths page showing list of user's learning paths and generation option
// Why: Central hub for viewing all learning paths and initiating new path generation
// Relevant Files: components/learning-paths/LearningPathsList.jsx, store/api/learningPathsApi.js

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useGetMyLearningPathsQuery } from '@/store/api/learningPathsApi';
import LearningPathsList from '@/components/learning-paths/LearningPathsList';
import GenerateLearningPathButton from '@/components/learning-paths/GenerateLearningPathButton';

export default function LearningPathsPage() {
  const router = useRouter();
  const { data, isLoading, error } = useGetMyLearningPathsQuery();

  const [view, setView] = useState('active'); // 'active', 'all', 'completed'

  const handleGenerateNew = () => {
    router.push('/app/learning-paths/generate');
  };

  const handleViewPath = (pathId) => {
    router.push(`/app/learning-paths/${pathId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              My Learning Paths
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Track your personalized learning journey powered by AI
            </p>
          </div>

          <GenerateLearningPathButton onClick={handleGenerateNew} />
        </div>

        {/* View Tabs */}
        <div className="flex gap-2 mb-6 border-b border-gray-200 dark:border-gray-700">
          {['active', 'all', 'completed'].map((tab) => (
            <button
              key={tab}
              onClick={() => setView(tab)}
              className={`px-4 py-2 font-medium transition-colors ${
                view === tab
                  ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Learning Paths List */}
        <LearningPathsList
          data={data}
          isLoading={isLoading}
          error={error}
          view={view}
          onViewPath={handleViewPath}
        />
      </div>
    </div>
  );
}
