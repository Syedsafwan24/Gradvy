// File: frontend/src/components/learning-paths/LearningPathsList.jsx
// Description: Displays list of learning paths with cards and filtering
// Why: Shows user's learning paths in a clean, organized card layout with status filtering
// Relevant Files: app/learning-paths/page.jsx, LearningPathCard.jsx

'use client';

import { BookOpen, Clock, Loader2, ArrowRight } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function LearningPathsList({ data, isLoading, error, view, onViewPath }) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600 mx-auto mb-3" />
          <p className="text-sm text-muted-foreground">Loading learning paths...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          {error?.data?.error?.message || 'Failed to load learning paths. Please try again later.'}
        </AlertDescription>
      </Alert>
    );
  }

  // Filter paths based on view
  const filteredPaths = data?.active_paths?.filter((path) => {
    if (view === 'active') return path.status === 'in_progress';
    if (view === 'completed') return path.status === 'completed';
    return true; // 'all' view
  }) || [];

  if (filteredPaths.length === 0) {
    return (
      <Card className="p-12">
        <div className="text-center">
          <BookOpen className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">
            No {view !== 'all' ? view : ''} learning paths yet
          </h3>
          <p className="text-sm text-muted-foreground">
            Generate your first AI-powered learning path to get started
          </p>
        </div>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
      {filteredPaths.map((path) => (
        <LearningPathCard
          key={path.path_id}
          path={path}
          onClick={() => onViewPath(path.path_id)}
        />
      ))}
    </div>
  );
}

function LearningPathCard({ path, onClick }) {
  const getStatusVariant = (status) => {
    switch (status) {
      case 'not_started':
        return 'secondary';
      case 'in_progress':
        return 'indigo';
      case 'completed':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'not_started':
        return 'Not Started';
      case 'in_progress':
        return 'In Progress';
      case 'completed':
        return 'Completed';
      default:
        return status;
    }
  };

  const getDifficultyVariant = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner':
        return 'success';
      case 'intermediate':
        return 'warning';
      case 'advanced':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  const progress = path.progress_percentage || 0;

  return (
    <Card 
      onClick={onClick}
      className="overflow-hidden cursor-pointer hover:shadow-md transition-shadow group"
    >
      {/* Progress Bar */}
      {path.status !== 'not_started' && (
        <div className="h-1 bg-muted">
          <div
            className="h-full bg-primary transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      <div className="p-4 sm:p-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <h3 className="text-base sm:text-lg font-semibold group-hover:text-primary transition-colors line-clamp-2 flex-1">
            {path.title}
          </h3>
          <Badge variant={getStatusVariant(path.status)}>
            {getStatusLabel(path.status)}
          </Badge>
        </div>

        {/* Description */}
        <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
          {path.description}
        </p>

        {/* Metadata */}
        <div className="flex flex-wrap items-center gap-3 text-sm mb-4">
          <div className="flex items-center gap-1 text-muted-foreground">
            <Clock className="w-4 h-4" />
            <span>{path.estimated_duration_hours}h</span>
          </div>
          <Badge variant={getDifficultyVariant(path.difficulty_level)} className="capitalize">
            {path.difficulty_level}
          </Badge>
        </div>

        {/* Progress */}
        {path.status !== 'not_started' && (
          <div className="flex items-center justify-between text-sm mb-3">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-semibold">
              {Math.round(progress)}%
            </span>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t text-sm">
          <span className="text-muted-foreground">
            {path.modules?.length || 0} modules
          </span>
          {path.status === 'not_started' && (
            <span className="text-primary font-medium flex items-center gap-1 group-hover:gap-2 transition-all">
              Start learning <ArrowRight className="w-4 h-4" />
            </span>
          )}
        </div>
      </div>
    </Card>
  );
}
