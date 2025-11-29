// File: frontend/src/components/learning-paths/LessonCard.jsx
// Description: Dispatcher component that routes to type-specific lesson cards
// Why: Provides content-type adaptive UI by delegating to specialized card components
// Relevant Files: ModulesList.jsx, lesson-cards/VideoLessonCard.jsx, lesson-cards/ArticleLessonCard.jsx

'use client';

import VideoLessonCard from './lesson-cards/VideoLessonCard';
import ArticleLessonCard from './lesson-cards/ArticleLessonCard';
import InteractiveLessonCard from './lesson-cards/InteractiveLessonCard';
import ProjectLessonCard from './lesson-cards/ProjectLessonCard';

/**
 * Main LessonCard dispatcher component.
 * Routes to type-specific card components based on lesson.type.
 *
 * Supported types:
 * - video: VideoLessonCard (red theme, large thumbnail, "Watch Video")
 * - article/reading: ArticleLessonCard (blue theme, icon-based, "Read Article")
 * - interactive/exercise: InteractiveLessonCard (green theme, difficulty badge, "Start Exercise")
 * - project: ProjectLessonCard (purple gradient, GitHub stars, "View Project")
 * - default: VideoLessonCard (fallback for unknown types)
 */
export default function LessonCard({ lesson, pathId, moduleId, lessonIndex, canStart }) {
  // Normalize lesson type to lowercase for consistent comparison
  const lessonType = (lesson.type || 'video').toLowerCase();

  // Route to appropriate type-specific card component
  switch (lessonType) {
    case 'article':
    case 'reading':
      return (
        <ArticleLessonCard
          lesson={lesson}
          pathId={pathId}
          moduleId={moduleId}
          lessonIndex={lessonIndex}
          canStart={canStart}
        />
      );

    case 'interactive':
    case 'exercise':
    case 'quiz':
      return (
        <InteractiveLessonCard
          lesson={lesson}
          pathId={pathId}
          moduleId={moduleId}
          lessonIndex={lessonIndex}
          canStart={canStart}
        />
      );

    case 'project':
    case 'tutorial':
      return (
        <ProjectLessonCard
          lesson={lesson}
          pathId={pathId}
          moduleId={moduleId}
          lessonIndex={lessonIndex}
          canStart={canStart}
        />
      );

    case 'video':
    default:
      // Default to video card for unknown types
      return (
        <VideoLessonCard
          lesson={lesson}
          pathId={pathId}
          moduleId={moduleId}
          lessonIndex={lessonIndex}
          canStart={canStart}
        />
      );
  }
}
