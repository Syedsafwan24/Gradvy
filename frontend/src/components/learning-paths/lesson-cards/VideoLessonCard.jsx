// File: frontend/src/components/learning-paths/lesson-cards/VideoLessonCard.jsx
// Description: Specialized card for video lessons with video-optimized UI and quiz integration
// Why: Provides video-specific visual design and UX (large thumbnail, watch button, red theme) with lock states and quiz functionality
// Relevant Files: LessonCard.jsx, ArticleLessonCard.jsx, ProgressBar.jsx, QuizModal.jsx

'use client';

import { useState } from 'react';
import { useUpdateProgressMutation } from '@/store/api/learningPathsApi';
import {
  PlayCircle,
  CheckCircle,
  Clock,
  ExternalLink,
  Video,
  Loader2,
  Lock,
  Award,
  AlertCircle
} from 'lucide-react';
import ProgressBar from '../ProgressBar';
import QuizModal from '../QuizModal';

export default function VideoLessonCard({ lesson, pathId, moduleId, lessonIndex, canStart }) {
  const [updateProgress, { isLoading }] = useUpdateProgressMutation();
  const [localProgress, setLocalProgress] = useState(lesson.progress_percentage || 0);
  const [isQuizModalOpen, setIsQuizModalOpen] = useState(false);

  const isCompleted = lesson.completed || localProgress === 100;
  const isLocked = lesson.is_locked || false;
  const quizRequired = lesson.quiz_required || false;
  const quizPassed = lesson.quiz_passed || false;
  const quizBestScore = lesson.quiz_best_score;
  const lockReason = lesson.lock_reason || '';

  // Handle marking lesson as complete or opening quiz
  const handleMarkComplete = async () => {
    if (!canStart || isLocked) return;

    // If quiz required and not passed, open quiz IMMEDIATELY (no alert)
    if (quizRequired && !quizPassed) {
      setIsQuizModalOpen(true);
      return; // Don't try to mark complete yet
    }

    // Quiz not required OR quiz already passed - mark complete
    await markLessonComplete();
  };

  // Separate function for marking lesson complete
  const markLessonComplete = async () => {
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

  // Callback when quiz is passed - auto-complete the lesson
  const handleQuizPassed = () => {
    markLessonComplete();
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
    <>
      {/* Quiz Modal */}
      <QuizModal
        open={isQuizModalOpen}
        onOpenChange={setIsQuizModalOpen}
        pathId={pathId}
        lessonId={lesson.lesson_id}
        lessonTitle={lesson.title}
        onQuizPassed={handleQuizPassed}
      />

      <div className={`relative bg-white dark:bg-gray-800 rounded-lg border-2 transition-all overflow-hidden ${
        isLocked
          ? 'border-gray-300 dark:border-gray-700'
          : isCompleted
            ? 'border-green-500 dark:border-green-400'
            : 'border-red-200 dark:border-red-800'
      } ${!canStart || isLocked ? 'opacity-50' : 'hover:shadow-lg hover:border-red-300'}`}>
      {/* Video Thumbnail - Larger for videos */}
      {lesson.thumbnail && (
        <div className="relative w-full h-48 bg-gray-900 overflow-hidden group">
          <img
            src={lesson.thumbnail}
            alt={lesson.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = 'https://via.placeholder.com/640x360/1F2937/EF4444?text=Video';
            }}
          />

          {/* Play overlay on hover */}
          {!isCompleted && canStart && (
            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              <div className="bg-red-600 rounded-full p-4">
                <PlayCircle className="w-12 h-12 text-white" />
              </div>
            </div>
          )}

          {/* Completed overlay */}
          {isCompleted && !isLocked && (
            <div className="absolute top-3 right-3 bg-green-600 text-white px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1">
              <CheckCircle className="w-4 h-4" />
              Watched
            </div>
          )}

          {/* Locked overlay */}
          {isLocked && (
            <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
              <div className="text-center text-white px-4">
                <Lock className="w-12 h-12 mx-auto mb-2" />
                <p className="text-sm font-medium">{lockReason || 'Complete previous lessons first'}</p>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="p-4">
        {/* Lesson Header */}
        <div className="flex items-start gap-3 mb-3">
          {/* Video Icon */}
          <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
            isCompleted
              ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
              : 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
          }`}>
            {isCompleted ? (
              <CheckCircle className="w-5 h-5" />
            ) : (
              <Video className="w-5 h-5" />
            )}
          </div>

          {/* Lesson Info */}
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
              {lesson.title}
            </h4>

            <div className="flex flex-wrap items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <span className="flex items-center gap-1">
                <Video className="w-4 h-4 text-red-500" />
                Video
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {lesson.duration_minutes > 0 ? `${lesson.duration_minutes} min` : 'Duration varies'}
              </span>
              <span className="text-xs px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-full font-medium">
                {lesson.platform || 'Video'}
              </span>

              {/* Quiz Status Badges */}
              {quizRequired && quizPassed && (
                <span className="text-xs px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full font-medium flex items-center gap-1">
                  <Award className="w-3 h-3" />
                  Quiz Passed {quizBestScore ? `(${quizBestScore.toFixed(0)}%)` : ''}
                </span>
              )}
              {quizRequired && !quizPassed && isCompleted && (
                <span className="text-xs px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded-full font-medium flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  Quiz Required
                </span>
              )}
              {isLocked && (
                <span className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-400 rounded-full font-medium flex items-center gap-1">
                  <Lock className="w-3 h-3" />
                  Locked
                </span>
              )}
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
            <ProgressBar progress={localProgress} height="h-2" color="red" />
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            {lesson.url && !isLocked && (
              <a
                href={lesson.url}
                target="_blank"
                rel="noopener noreferrer"
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors text-sm font-medium flex-1 justify-center ${
                  isCompleted
                    ? 'bg-gray-600 hover:bg-gray-700 text-white'
                    : 'bg-red-600 hover:bg-red-700 text-white'
                }`}
              >
                {isCompleted ? (
                  <>
                    <ExternalLink className="w-4 h-4" />
                    Rewatch Video
                  </>
                ) : (
                  <>
                    <PlayCircle className="w-4 h-4" />
                    Watch Video
                  </>
                )}
              </a>
            )}

            {canStart && !isCompleted && !isLocked && (
              <button
                onClick={handleMarkComplete}
                disabled={isLoading}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors text-sm font-medium ${
                  quizRequired && !quizPassed
                    ? 'bg-purple-600 hover:bg-purple-700 text-white'
                    : 'bg-green-600 hover:bg-green-700 text-white'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
                title={quizRequired && !quizPassed ? 'Take quiz to complete lesson' : 'Mark as complete'}
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : quizRequired && !quizPassed ? (
                  <Award className="w-4 h-4" />
                ) : (
                  <CheckCircle className="w-4 h-4" />
                )}
                {quizRequired && !quizPassed ? 'Take Quiz' : 'Complete'}
              </button>
            )}

            {isCompleted && !isLocked && (
              <div className="flex items-center gap-2 text-green-600 dark:text-green-400 text-sm font-medium">
                <CheckCircle className="w-4 h-4" />
                Completed
              </div>
            )}

            {isLocked && (
              <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 text-sm font-medium px-4 py-2">
                <Lock className="w-4 h-4" />
                Locked
              </div>
            )}
          </div>

          {/* Quiz Retake Button - Only show if quiz already passed */}
          {canStart && isCompleted && quizRequired && quizPassed && !isLocked && (
            <button
              onClick={() => setIsQuizModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors text-sm font-medium justify-center bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 hover:bg-blue-200"
            >
              <Award className="w-4 h-4" />
              Retake Quiz {quizBestScore ? `(${quizBestScore.toFixed(0)}%)` : ''}
            </button>
          )}
        </div>

        {/* Progress Slider (if in progress) */}
        {canStart && localProgress > 0 && localProgress < 100 && !isLocked && (
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
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-red-600"
            />
          </div>
        )}
      </div>
    </div>
    </>
  );
}
