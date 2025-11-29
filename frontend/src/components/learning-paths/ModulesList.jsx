// File: frontend/src/components/learning-paths/ModulesList.jsx
// Description: Accordion list of modules with lessons
// Why: Displays structured learning path modules with expandable lessons
// Relevant Files: LessonCard.jsx, app/learning-paths/[pathId]/page.jsx

'use client';

import { useState } from 'react';
import { ChevronDown, ChevronRight, Lock, CheckCircle, BookOpen } from 'lucide-react';
import LessonCard from './LessonCard';
import ProgressBar from './ProgressBar';

export default function ModulesList({ modules = [], pathId, status }) {
  const [expandedModules, setExpandedModules] = useState(new Set([modules[0]?.module_id]));

  const toggleModule = (moduleId) => {
    setExpandedModules((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(moduleId)) {
        newSet.delete(moduleId);
      } else {
        newSet.add(moduleId);
      }
      return newSet;
    });
  };

  if (!modules || modules.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 text-center">
        <BookOpen className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
        <p className="text-gray-600 dark:text-gray-400">No modules available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Learning Modules
      </h2>

      {modules.map((module, index) => {
        const isExpanded = expandedModules.has(module.module_id);
        const moduleProgress = module.progress_percentage || 0;
        const completedLessons = module.completed_lessons || 0;
        const totalLessons = module.total_lessons || module.lessons?.length || 0;
        const isCompleted = moduleProgress === 100;
        const isLocked = module.skipped || false;

        return (
          <div
            key={module.module_id}
            className={`bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden border-2 transition-all ${
              isExpanded
                ? 'border-blue-500 dark:border-blue-400'
                : 'border-gray-200 dark:border-gray-700'
            } ${isLocked ? 'opacity-60' : ''}`}
          >
            {/* Module Header */}
            <button
              onClick={() => !isLocked && toggleModule(module.module_id)}
              className="w-full p-6 flex items-start gap-4 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors text-left"
              disabled={isLocked}
            >
              {/* Module Number */}
              <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg ${
                isCompleted
                  ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                  : isLocked
                  ? 'bg-gray-200 dark:bg-gray-700 text-gray-500'
                  : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
              }`}>
                {isCompleted ? (
                  <CheckCircle className="w-6 h-6" />
                ) : isLocked ? (
                  <Lock className="w-5 h-5" />
                ) : (
                  module.order || index + 1
                )}
              </div>

              {/* Module Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-4 mb-2">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                    {module.title}
                  </h3>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {isLocked && (
                      <span className="text-xs px-2 py-1 bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full">
                        Skipped
                      </span>
                    )}
                    {!isLocked && (
                      isExpanded ? (
                        <ChevronDown className="w-5 h-5 text-gray-500" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-500" />
                      )
                    )}
                  </div>
                </div>

                <p className="text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                  {module.description}
                </p>

                {/* Module Meta */}
                <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-3">
                  <span>{totalLessons} lessons</span>
                  <span>•</span>
                  <span>~{module.estimated_hours} hours</span>
                  {status !== 'not_started' && (
                    <>
                      <span>•</span>
                      <span className="font-medium">
                        {completedLessons}/{totalLessons} completed
                      </span>
                    </>
                  )}
                </div>

                {/* Progress Bar */}
                {status !== 'not_started' && !isLocked && (
                  <ProgressBar progress={moduleProgress} height="h-2" />
                )}
              </div>
            </button>

            {/* Module Lessons */}
            {isExpanded && !isLocked && (
              <div className="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750">
                <div className="p-6 space-y-3">
                  {module.lessons && module.lessons.length > 0 ? (
                    module.lessons.map((lesson, lessonIndex) => (
                      <LessonCard
                        key={lesson.lesson_id}
                        lesson={lesson}
                        pathId={pathId}
                        moduleId={module.module_id}
                        lessonIndex={lessonIndex}
                        canStart={status !== 'not_started'}
                      />
                    ))
                  ) : (
                    <p className="text-center text-gray-500 dark:text-gray-400 py-4">
                      No lessons available for this module
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
