// File: frontend/src/components/learning-paths/QuizModal.jsx
// Description: Modal component for taking quizzes, submitting answers, and viewing results
// Why: Provides interactive quiz interface with multiple question types and real-time grading
// Relevant Files: learningPathsApi.js, LessonCard.jsx, ModulesList.jsx, ui/dialog.jsx

'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Alert } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  useGetQuizQuery,
  useStartQuizAttemptMutation,
  useSubmitQuizMutation,
  useGetQuizAttemptsQuery,
} from '@/store/api/learningPathsApi';

/**
 * QuizModal Component
 *
 * Handles the complete quiz workflow:
 * 1. Load quiz questions (GET /api/quizzes/{pathId}/{lessonId}/)
 * 2. Start quiz attempt (POST /api/quizzes/{quizId}/start/)
 * 3. Display questions with appropriate UI for each type
 * 4. Track time and collect answers
 * 5. Submit answers for grading (POST /api/quizzes/attempts/{attemptId}/submit/)
 * 6. Display results with explanations and retake option
 *
 * @param {boolean} open - Whether modal is open
 * @param {function} onOpenChange - Callback to close modal
 * @param {string} pathId - Learning path ID
 * @param {string} lessonId - Lesson ID
 * @param {string} lessonTitle - Lesson title for display
 * @param {function} onQuizPassed - Optional callback when quiz is passed (auto-completes lesson)
 */
export default function QuizModal({ open, onOpenChange, pathId, lessonId, lessonTitle, onQuizPassed }) {
  // ========================================================================
  // State Management
  // ========================================================================

  const [quizState, setQuizState] = useState('loading'); // loading, ready, taking, submitting, results
  const [attemptId, setAttemptId] = useState(null);
  const [answers, setAnswers] = useState({}); // { questionId: userAnswer }
  const [questionTimes, setQuestionTimes] = useState({}); // { questionId: startTime }
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [quizStartTime, setQuizStartTime] = useState(null);
  const [results, setResults] = useState(null);

  // ========================================================================
  // API Hooks
  // ========================================================================

  // Fetch quiz data (questions, passing score, etc.)
  const { data: quizData, isLoading: isLoadingQuiz, error: quizError } = useGetQuizQuery(
    { pathId, lessonId },
    { skip: !open }
  );

  // Fetch previous attempts for statistics
  const { data: attemptsData } = useGetQuizAttemptsQuery(
    { pathId, lessonId },
    { skip: !open }
  );

  // Start quiz attempt mutation
  const [startQuizAttempt, { isLoading: isStarting }] = useStartQuizAttemptMutation();

  // Submit quiz mutation
  const [submitQuiz, { isLoading: isSubmitting }] = useSubmitQuizMutation();

  // ========================================================================
  // Effects
  // ========================================================================

  // Reset state when modal opens/closes
  useEffect(() => {
    if (open) {
      setQuizState('loading');
      setAnswers({});
      setQuestionTimes({});
      setCurrentQuestionIndex(0);
      setResults(null);
      setAttemptId(null);
      setQuizStartTime(null);
    }
  }, [open]);

  // Update state when quiz loads
  useEffect(() => {
    if (quizData && quizState === 'loading') {
      setQuizState('ready');
    }
  }, [quizData, quizState]);

  // Track time for current question
  useEffect(() => {
    if (quizState === 'taking' && quizData?.questions?.[currentQuestionIndex]) {
      const questionId = quizData.questions[currentQuestionIndex].id;
      if (!questionTimes[questionId]) {
        setQuestionTimes(prev => ({ ...prev, [questionId]: Date.now() }));
      }
    }
  }, [quizState, currentQuestionIndex, quizData, questionTimes]);

  // ========================================================================
  // Event Handlers
  // ========================================================================

  /**
   * Start the quiz attempt
   */
  const handleStartQuiz = async () => {
    try {
      const result = await startQuizAttempt(quizData.id).unwrap();
      setAttemptId(result.attempt_id);
      setQuizStartTime(Date.now());
      setQuizState('taking');
    } catch (error) {
      console.error('Failed to start quiz:', error);
      alert('Failed to start quiz. Please try again.');
    }
  };

  /**
   * Handle answer change for current question
   */
  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }));
  };

  /**
   * Navigate to next question
   */
  const handleNextQuestion = () => {
    if (currentQuestionIndex < quizData.questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  /**
   * Navigate to previous question
   */
  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  /**
   * Submit quiz for grading
   */
  const handleSubmitQuiz = async () => {
    // Validate all questions answered
    const unansweredQuestions = quizData.questions.filter(q => !answers[q.id]);
    if (unansweredQuestions.length > 0) {
      const confirmSubmit = window.confirm(
        `You have ${unansweredQuestions.length} unanswered question(s). Submit anyway?`
      );
      if (!confirmSubmit) return;
    }

    setQuizState('submitting');

    try {
      // Calculate time taken for each question
      const answersPayload = quizData.questions.map(question => {
        const questionId = question.id;
        const userAnswer = answers[questionId] || '';
        const startTime = questionTimes[questionId] || quizStartTime;
        const timeTaken = Math.floor((Date.now() - startTime) / 1000); // seconds

        return {
          question_id: questionId,
          user_answer: userAnswer,
          time_taken_seconds: timeTaken
        };
      });

      // Submit quiz
      const result = await submitQuiz({
        attemptId,
        answers: answersPayload
      }).unwrap();

      setResults(result);
      setQuizState('results');

      // If quiz passed, trigger callback to auto-complete lesson
      if (result.passed && onQuizPassed) {
        onQuizPassed();

        // Auto-close modal after 2 seconds to show success
        setTimeout(() => {
          onOpenChange(false);
        }, 2000);
      }
    } catch (error) {
      console.error('Failed to submit quiz:', error);
      alert('Failed to submit quiz. Please try again.');
      setQuizState('taking');
    }
  };

  /**
   * Retake quiz (start new attempt)
   */
  const handleRetake = () => {
    setAnswers({});
    setQuestionTimes({});
    setCurrentQuestionIndex(0);
    setResults(null);
    setAttemptId(null);
    setQuizStartTime(null);
    setQuizState('ready');
  };

  /**
   * Close modal and refresh parent
   */
  const handleClose = () => {
    onOpenChange(false);
  };

  // ========================================================================
  // Render Helpers
  // ========================================================================

  /**
   * Render question based on type
   */
  const renderQuestion = (question) => {
    const questionId = question.id;
    const userAnswer = answers[questionId] || '';

    switch (question.question_type) {
      case 'multiple_choice':
        return (
          <div className="space-y-4">
            <p className="text-base font-medium">{question.question_text}</p>
            <RadioGroup value={userAnswer} onValueChange={(val) => handleAnswerChange(questionId, val)}>
              {question.options?.options?.map((option, idx) => (
                <div key={idx} className="flex items-center space-x-2">
                  <RadioGroupItem value={option} id={`q${questionId}-opt${idx}`} />
                  <Label htmlFor={`q${questionId}-opt${idx}`} className="cursor-pointer">
                    {option}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </div>
        );

      case 'true_false':
        return (
          <div className="space-y-4">
            <p className="text-base font-medium">{question.question_text}</p>
            <RadioGroup value={userAnswer} onValueChange={(val) => handleAnswerChange(questionId, val)}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="True" id={`q${questionId}-true`} />
                <Label htmlFor={`q${questionId}-true`} className="cursor-pointer">True</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="False" id={`q${questionId}-false`} />
                <Label htmlFor={`q${questionId}-false`} className="cursor-pointer">False</Label>
              </div>
            </RadioGroup>
          </div>
        );

      case 'short_answer':
        return (
          <div className="space-y-4">
            <p className="text-base font-medium">{question.question_text}</p>
            <Textarea
              value={userAnswer}
              onChange={(e) => handleAnswerChange(questionId, e.target.value)}
              placeholder="Type your answer here..."
              rows={3}
              className="w-full"
            />
          </div>
        );

      case 'code':
        return (
          <div className="space-y-4">
            <p className="text-base font-medium">{question.question_text}</p>
            <Textarea
              value={userAnswer}
              onChange={(e) => handleAnswerChange(questionId, e.target.value)}
              placeholder="Write your code here..."
              rows={8}
              className="w-full font-mono text-sm"
            />
          </div>
        );

      default:
        return (
          <div className="space-y-4">
            <p className="text-base font-medium">{question.question_text}</p>
            <Textarea
              value={userAnswer}
              onChange={(e) => handleAnswerChange(questionId, e.target.value)}
              placeholder="Type your answer..."
              rows={3}
              className="w-full"
            />
          </div>
        );
    }
  };

  /**
   * Render quiz results
   */
  const renderResults = () => {
    if (!results) return null;

    const passed = results.passed;
    const scorePercentage = results.score_percentage?.toFixed(1) || 0;
    const passingScore = results.passing_score_percentage || 70;

    return (
      <div className="space-y-6">
        {/* Score Summary */}
        <div className="text-center space-y-4">
          <div className={`text-6xl font-bold ${passed ? 'text-green-600' : 'text-red-600'}`}>
            {scorePercentage}%
          </div>
          <div>
            <Badge variant={passed ? 'default' : 'destructive'} className="text-lg px-4 py-2">
              {passed ? '✓ Passed' : '✗ Failed'}
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            Passing score: {passingScore}% | Your best: {results.best_score_percentage?.toFixed(1)}%
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-green-600">{results.correct_answers}</div>
            <div className="text-xs text-muted-foreground">Correct</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-red-600">{results.incorrect_answers}</div>
            <div className="text-xs text-muted-foreground">Incorrect</div>
          </div>
          <div>
            <div className="text-2xl font-bold">{results.total_questions}</div>
            <div className="text-xs text-muted-foreground">Total</div>
          </div>
        </div>

        {/* Question Breakdown */}
        <div className="space-y-3 max-h-96 overflow-y-auto">
          <h4 className="font-semibold text-sm">Question Breakdown</h4>
          {results.questions_breakdown?.map((q, idx) => (
            <div key={q.question_id} className={`p-4 rounded-lg border ${q.is_correct ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
              <div className="flex items-start justify-between mb-2">
                <span className="font-medium text-sm">Question {idx + 1}</span>
                <Badge variant={q.is_correct ? 'default' : 'destructive'} className="text-xs">
                  {q.is_correct ? '✓' : '✗'} {q.points_earned}/{q.points_possible} pts
                </Badge>
              </div>
              <p className="text-sm mb-2">{q.question_text}</p>
              <div className="space-y-1 text-xs">
                <div>
                  <span className="font-medium">Your answer:</span> {q.user_answer || '(no answer)'}
                </div>
                {!q.is_correct && (
                  <div className="text-green-700">
                    <span className="font-medium">Correct answer:</span> {q.correct_answer}
                  </div>
                )}
                {q.explanation && (
                  <div className="text-muted-foreground italic mt-2">
                    {q.explanation}
                  </div>
                )}
                {q.feedback && (
                  <div className="text-blue-700 mt-1">
                    {q.feedback}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Next Lesson Status */}
        {results.next_lesson_unlocked && (
          <Alert className="bg-green-50 border-green-200">
            <div className="text-green-800">
              <strong>Congratulations!</strong> You've unlocked the next lesson.
            </div>
          </Alert>
        )}
      </div>
    );
  };

  // ========================================================================
  // Render States
  // ========================================================================

  // Loading state
  if (isLoadingQuiz || quizState === 'loading') {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Loading Quiz...</DialogTitle>
          </DialogHeader>
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  // Error state
  if (quizError) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Error Loading Quiz</DialogTitle>
            <DialogDescription>
              Failed to load quiz. Please try again later.
            </DialogDescription>
          </DialogHeader>
          <Alert variant="destructive">
            {quizError?.data?.message || 'An error occurred while loading the quiz.'}
          </Alert>
          <DialogFooter>
            <Button onClick={handleClose}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  }

  // Ready to start state
  if (quizState === 'ready') {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Quiz: {lessonTitle}</DialogTitle>
            <DialogDescription>
              Test your knowledge of this lesson
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Quiz Info */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Questions:</span>
                <span className="text-sm">{quizData?.num_questions || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Passing Score:</span>
                <span className="text-sm">{quizData?.passing_score_percentage || 70}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Platform:</span>
                <span className="text-sm capitalize">{quizData?.lesson_platform || 'Unknown'}</span>
              </div>
            </div>

            {/* Previous Attempts */}
            {attemptsData && attemptsData.total_attempts > 0 && (
              <div className="border-t pt-4">
                <h4 className="text-sm font-medium mb-2">Your Statistics</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Attempts:</span>{' '}
                    <span className="font-medium">{attemptsData.total_attempts}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Best Score:</span>{' '}
                    <span className="font-medium">
                      {attemptsData.best_score_percentage?.toFixed(1)}%
                    </span>
                  </div>
                  <div className="col-span-2">
                    <span className="text-muted-foreground">Status:</span>{' '}
                    <Badge variant={attemptsData.passed ? 'default' : 'secondary'}>
                      {attemptsData.passed ? 'Passed' : 'Not Passed'}
                    </Badge>
                  </div>
                </div>
              </div>
            )}

            {/* Instructions */}
            <Alert>
              <div className="text-sm">
                <strong>Instructions:</strong>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>Answer all questions to the best of your ability</li>
                  <li>You need {quizData?.passing_score_percentage || 70}% to pass and unlock the next lesson</li>
                  <li>You can retake the quiz as many times as needed</li>
                  <li>Your best score will be saved</li>
                </ul>
              </div>
            </Alert>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={handleClose}>Cancel</Button>
            <Button onClick={handleStartQuiz} disabled={isStarting}>
              {isStarting ? 'Starting...' : 'Start Quiz'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  }

  // Taking quiz state
  if (quizState === 'taking' || quizState === 'submitting') {
    const currentQuestion = quizData?.questions?.[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / quizData.questions.length) * 100;
    const answeredCount = Object.keys(answers).length;

    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              Question {currentQuestionIndex + 1} of {quizData.questions.length}
            </DialogTitle>
            <DialogDescription>
              {answeredCount} of {quizData.questions.length} answered
            </DialogDescription>
          </DialogHeader>

          {/* Progress Bar */}
          <Progress value={progress} className="w-full" />

          {/* Question */}
          <div className="py-6">
            {currentQuestion && (
              <div className="space-y-4">
                {/* Question Metadata */}
                <div className="flex items-center gap-2 mb-4">
                  <Badge variant="outline">{currentQuestion.question_type.replace('_', ' ')}</Badge>
                  <Badge variant="secondary">{currentQuestion.difficulty}</Badge>
                  <span className="text-xs text-muted-foreground ml-auto">
                    {currentQuestion.points} {currentQuestion.points === 1 ? 'point' : 'points'}
                  </span>
                </div>

                {/* Question Content */}
                {renderQuestion(currentQuestion)}
              </div>
            )}
          </div>

          {/* Navigation */}
          <DialogFooter className="flex justify-between items-center">
            <Button
              variant="outline"
              onClick={handlePreviousQuestion}
              disabled={currentQuestionIndex === 0}
            >
              Previous
            </Button>

            <span className="text-sm text-muted-foreground">
              {answeredCount}/{quizData.questions.length} answered
            </span>

            {currentQuestionIndex < quizData.questions.length - 1 ? (
              <Button onClick={handleNextQuestion}>
                Next
              </Button>
            ) : (
              <Button
                onClick={handleSubmitQuiz}
                disabled={quizState === 'submitting'}
                variant="default"
              >
                {quizState === 'submitting' ? 'Submitting...' : 'Submit Quiz'}
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  }

  // Results state
  if (quizState === 'results') {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Quiz Results</DialogTitle>
            <DialogDescription>
              {lessonTitle}
            </DialogDescription>
          </DialogHeader>

          {renderResults()}

          <DialogFooter className="flex justify-between">
            <Button variant="outline" onClick={handleRetake}>
              Retake Quiz
            </Button>
            <Button onClick={handleClose}>
              {results?.passed ? 'Continue to Next Lesson' : 'Close'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  }

  return null;
}
