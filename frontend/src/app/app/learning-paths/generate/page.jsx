// File: frontend/src/app/learning-paths/generate/page.jsx
// Description: Learning path generation page with form for user preferences
// Why: Allows users to generate personalized learning paths using AI based on their goals and preferences
// Relevant Files: components/learning-paths/GeneratePathForm.jsx, store/api/learningPathsApi.js

'use client';

import { useRouter } from 'next/navigation';
import GeneratePathForm from '@/components/learning-paths/GeneratePathForm';
import { ArrowLeft } from 'lucide-react';

export default function GenerateLearningPathPage() {
  const router = useRouter();

  const handleBack = () => {
    router.back();
  };

  const handleSuccess = (pathId) => {
    // Redirect to the newly generated learning path
    router.push(`/app/learning-paths/${pathId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Back Button */}
        <button
          onClick={handleBack}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Learning Paths
        </button>

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-3">
            Generate Your Learning Path
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Tell us about your learning goals and preferences, and our AI will create a personalized learning path tailored just for you
          </p>
        </div>

        {/* Generation Form */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
          <GeneratePathForm onSuccess={handleSuccess} />
        </div>

        {/* Info Section */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <div className="text-blue-600 dark:text-blue-400 font-semibold mb-2">
              AI-Powered
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Uses advanced AI to create paths optimized for your learning style
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <div className="text-blue-600 dark:text-blue-400 font-semibold mb-2">
              Personalized
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Tailored to your experience level, pace, and time availability
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <div className="text-blue-600 dark:text-blue-400 font-semibold mb-2">
              Customizable
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Modify your path anytime by skipping modules or swapping resources
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
