// File: frontend/src/app/learning-paths/page.jsx
// Description: Main learning paths page showing list of user's learning paths and generation option
// Why: Central hub for viewing all learning paths and initiating new path generation
// Relevant Files: components/learning-paths/LearningPathsList.jsx, store/api/learningPathsApi.js

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Sparkles } from 'lucide-react';
import { useGetMyLearningPathsQuery } from '@/store/api/learningPathsApi';
import LearningPathsList from '@/components/learning-paths/LearningPathsList';
import PageLayout from '@/components/layouts/PageLayout';
import { Button } from '@/components/ui/button';

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
    <PageLayout
      title="My Learning Paths"
      description="Track your personalized learning journey powered by AI"
      actions={
        <Button 
          onClick={handleGenerateNew} 
          className="h-11 gap-2"
        >
          <Sparkles className="w-4 h-4" />
          Generate New Path
        </Button>
      }
    >
      {/* View Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-200 dark:border-gray-700">
        {['active', 'all', 'completed'].map((tab) => (
          <button
            key={tab}
            onClick={() => setView(tab)}
            className={`px-4 py-2 text-sm font-medium transition-colors rounded-t-md ${
              view === tab
                ? 'text-primary-600 dark:text-primary-400 border-b-2 border-primary-600 dark:border-primary-400'
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
    </PageLayout>
  );
}
