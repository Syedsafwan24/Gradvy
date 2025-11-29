# File: backend/core/apps/learning_content/api/quiz_grader.py
# Description: Quiz grading logic for different question types
# Why: Handles answer validation and scoring for MC, T/F, short answer, and code questions
# Relevant Files: quiz_views.py, models.py, serializers.py

import logging
from typing import Dict, Any, List
from datetime import datetime
from django.db import transaction
from django.utils import timezone

from apps.learning_content.models import QuizAttempt, QuizQuestion, QuestionResponse

logger = logging.getLogger(__name__)


class QuizGrader:
    """
    Handles quiz grading for different question types.

    Supports:
    - Multiple Choice (MC): Exact match with correct option index
    - True/False (T/F): Boolean comparison
    - Short Answer: Keyword matching with fuzzy logic
    - Code: Test case execution (placeholder for future implementation)
    """

    @classmethod
    def grade_quiz_attempt(
        cls,
        attempt: QuizAttempt,
        answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Grade a quiz attempt and update the database.

        Args:
            attempt: QuizAttempt instance
            answers: List of answer dictionaries from request

        Returns:
            Dictionary with grading results for QuizResultSerializer
        """
        try:
            with transaction.atomic():
                # Get all questions for this quiz
                questions = list(attempt.quiz.questions.all().order_by('order'))
                questions_by_id = {q.id: q for q in questions}

                # Track grading results
                total_points_earned = 0
                total_points_possible = sum(q.points for q in questions)
                correct_count = 0
                incorrect_count = 0
                questions_breakdown = []

                # Grade each answer
                for answer_data in answers:
                    question_id = answer_data['question_id']
                    user_answer = answer_data['user_answer']
                    time_taken = answer_data.get('time_taken_seconds')

                    # Get question
                    question = questions_by_id.get(question_id)
                    if not question:
                        logger.warning(f"Question {question_id} not found in quiz {attempt.quiz.id}")
                        continue

                    # Grade based on question type
                    is_correct, points_earned, feedback = cls._grade_question(
                        question=question,
                        user_answer=user_answer
                    )

                    # Create QuestionResponse
                    response = QuestionResponse.objects.create(
                        attempt=attempt,
                        question=question,
                        user_answer=user_answer,
                        is_correct=is_correct,
                        points_earned=points_earned,
                        time_taken_seconds=time_taken,
                        ai_feedback=feedback
                    )

                    # Update totals
                    total_points_earned += points_earned
                    if is_correct:
                        correct_count += 1
                    else:
                        incorrect_count += 1

                    # Add to breakdown
                    questions_breakdown.append({
                        'question_id': question.id,
                        'question_text': question.question_text,
                        'question_type': question.question_type,
                        'user_answer': user_answer,
                        'correct_answer': question.correct_answer,
                        'is_correct': is_correct,
                        'points_earned': points_earned,
                        'points_possible': question.points,
                        'explanation': question.explanation,
                        'feedback': feedback
                    })

                # Calculate final score percentage
                score_percentage = (total_points_earned / total_points_possible * 100) if total_points_possible > 0 else 0

                # Update attempt
                attempt.status = 'completed'
                attempt.completed_at = timezone.now()
                attempt.score_percentage = score_percentage
                attempt.total_points_earned = total_points_earned
                attempt.total_points_possible = total_points_possible
                # passed field is auto-calculated in model's save() method
                attempt.save()

                # Get best score across all attempts
                best_score = QuizAttempt.objects.filter(
                    quiz=attempt.quiz,
                    user=attempt.user,
                    status='completed'
                ).order_by('-score_percentage').first()

                best_score_pct = best_score.score_percentage if best_score else score_percentage

                logger.info(f"✅ Graded quiz attempt {attempt.id}: {score_percentage:.1f}% ({total_points_earned}/{total_points_possible} points)")

                # Return results
                return {
                    'attempt': {
                        'id': attempt.id,
                        'quiz_id': attempt.quiz.id,
                        'attempt_number': attempt.attempt_number,
                        'status': attempt.status,
                        'started_at': attempt.started_at,
                        'completed_at': attempt.completed_at,
                        'time_taken_seconds': attempt.time_taken_seconds,
                        'score_percentage': attempt.score_percentage,
                        'total_points_earned': attempt.total_points_earned,
                        'total_points_possible': attempt.total_points_possible,
                        'passed': attempt.passed,
                        'is_best_attempt': attempt.is_best_attempt,
                        'responses': []  # Populated separately
                    },
                    'passed': attempt.passed,
                    'score_percentage': score_percentage,
                    'passing_score_percentage': attempt.quiz.passing_score_percentage,
                    'questions_breakdown': questions_breakdown,
                    'total_questions': len(questions),
                    'correct_answers': correct_count,
                    'incorrect_answers': incorrect_count,
                    'time_taken_seconds': attempt.time_taken_seconds or 0,
                    'can_retake': True,  # Unlimited retakes allowed
                    'next_lesson_unlocked': attempt.passed,  # Unlock next lesson if passed
                    'best_score_percentage': best_score_pct
                }

        except Exception as e:
            logger.error(f"Error grading quiz attempt {attempt.id}: {e}", exc_info=True)
            raise

    @classmethod
    def _grade_question(
        cls,
        question: QuizQuestion,
        user_answer: str
    ) -> tuple[bool, int, str]:
        """
        Grade a single question based on its type.

        Args:
            question: QuizQuestion instance
            user_answer: User's answer (string)

        Returns:
            Tuple of (is_correct, points_earned, feedback)
        """
        question_type = question.question_type

        if question_type == 'multiple_choice':
            return cls._grade_multiple_choice(question, user_answer)
        elif question_type == 'true_false':
            return cls._grade_true_false(question, user_answer)
        elif question_type == 'short_answer':
            return cls._grade_short_answer(question, user_answer)
        elif question_type == 'code':
            return cls._grade_code(question, user_answer)
        else:
            # Default: exact match
            return cls._grade_exact_match(question, user_answer)

    @classmethod
    def _grade_multiple_choice(
        cls,
        question: QuizQuestion,
        user_answer: str
    ) -> tuple[bool, int, str]:
        """
        Grade multiple choice question.

        Compares user's answer with correct answer.
        Options stored in question.options as:
        {"options": ["A", "B", "C", "D"], "correct_index": 2}
        """
        try:
            correct_answer = question.correct_answer.strip().lower()
            user_answer_clean = user_answer.strip().lower()

            # Check exact match
            is_correct = correct_answer == user_answer_clean

            # Also check if user answered by index
            options = question.options.get('options', [])
            correct_index = question.options.get('correct_index', 0)

            if not is_correct and options and user_answer_clean.isdigit():
                # User might have answered with index
                user_index = int(user_answer_clean)
                is_correct = user_index == correct_index

            points = question.points if is_correct else 0
            feedback = "Correct!" if is_correct else f"Incorrect. The correct answer is: {question.correct_answer}"

            return is_correct, points, feedback

        except Exception as e:
            logger.error(f"Error grading MC question {question.id}: {e}")
            return False, 0, "Error grading question"

    @classmethod
    def _grade_true_false(
        cls,
        question: QuizQuestion,
        user_answer: str
    ) -> tuple[bool, int, str]:
        """
        Grade true/false question.

        Accepts: true, false, t, f, yes, no (case-insensitive)
        """
        try:
            correct_answer = question.correct_answer.strip().lower()
            user_answer_clean = user_answer.strip().lower()

            # Normalize answers
            true_values = ['true', 't', 'yes', 'y', '1']
            false_values = ['false', 'f', 'no', 'n', '0']

            user_is_true = user_answer_clean in true_values
            user_is_false = user_answer_clean in false_values

            correct_is_true = correct_answer in true_values
            correct_is_false = correct_answer in false_values

            is_correct = (user_is_true and correct_is_true) or (user_is_false and correct_is_false)

            points = question.points if is_correct else 0
            feedback = "Correct!" if is_correct else f"Incorrect. The correct answer is: {question.correct_answer}"

            return is_correct, points, feedback

        except Exception as e:
            logger.error(f"Error grading T/F question {question.id}: {e}")
            return False, 0, "Error grading question"

    @classmethod
    def _grade_short_answer(
        cls,
        question: QuizQuestion,
        user_answer: str
    ) -> tuple[bool, int, str]:
        """
        Grade short answer question.

        Uses keyword matching with partial credit.
        Options may contain keywords:
        {"keywords": ["key1", "key2"], "exact_match": false}
        """
        try:
            correct_answer = question.correct_answer.strip().lower()
            user_answer_clean = user_answer.strip().lower()

            # Check exact match first
            if correct_answer == user_answer_clean:
                return True, question.points, "Perfect answer!"

            # Check keyword matching
            options = question.options or {}
            keywords = options.get('keywords', [])
            exact_match_required = options.get('exact_match', False)

            if exact_match_required:
                # Exact match required
                is_correct = correct_answer == user_answer_clean
                points = question.points if is_correct else 0
                feedback = "Correct!" if is_correct else f"Incorrect. Expected: {question.correct_answer}"
                return is_correct, points, feedback

            # Keyword-based partial credit
            if keywords:
                matched_keywords = sum(1 for kw in keywords if kw.lower() in user_answer_clean)
                match_percentage = matched_keywords / len(keywords)

                if match_percentage >= 0.7:
                    # 70%+ keywords matched - full credit
                    return True, question.points, "Good answer!"
                elif match_percentage >= 0.4:
                    # 40-70% keywords matched - partial credit
                    partial_points = int(question.points * match_percentage)
                    return False, partial_points, f"Partial credit. Expected keywords: {', '.join(keywords)}"
                else:
                    # Less than 40% - no credit
                    return False, 0, f"Incorrect. Expected keywords: {', '.join(keywords)}"

            # No keywords defined, use fuzzy string matching
            # Simple contains check
            is_correct = correct_answer in user_answer_clean or user_answer_clean in correct_answer
            points = question.points if is_correct else 0
            feedback = "Close enough!" if is_correct else f"Incorrect. Expected: {question.correct_answer}"

            return is_correct, points, feedback

        except Exception as e:
            logger.error(f"Error grading short answer question {question.id}: {e}")
            return False, 0, "Error grading question"

    @classmethod
    def _grade_code(
        cls,
        question: QuizQuestion,
        user_answer: str
    ) -> tuple[bool, int, str]:
        """
        Grade code question.

        PLACEHOLDER: Future implementation will execute test cases.
        For now, uses simple string matching.
        """
        try:
            # TODO: Implement proper code execution and test case evaluation
            # For now, just check if user provided code
            if not user_answer or len(user_answer.strip()) < 10:
                return False, 0, "Please provide a valid code solution"

            # Placeholder: give partial credit for any code submission
            logger.warning(f"Code grading not fully implemented for question {question.id}")
            return True, int(question.points * 0.5), "Code submitted (partial credit - manual review recommended)"

        except Exception as e:
            logger.error(f"Error grading code question {question.id}: {e}")
            return False, 0, "Error grading question"

    @classmethod
    def _grade_exact_match(
        cls,
        question: QuizQuestion,
        user_answer: str
    ) -> tuple[bool, int, str]:
        """
        Grade with exact string matching (fallback).
        """
        try:
            correct_answer = question.correct_answer.strip().lower()
            user_answer_clean = user_answer.strip().lower()

            is_correct = correct_answer == user_answer_clean
            points = question.points if is_correct else 0
            feedback = "Correct!" if is_correct else f"Incorrect. The correct answer is: {question.correct_answer}"

            return is_correct, points, feedback

        except Exception as e:
            logger.error(f"Error with exact match grading for question {question.id}: {e}")
            return False, 0, "Error grading question"
