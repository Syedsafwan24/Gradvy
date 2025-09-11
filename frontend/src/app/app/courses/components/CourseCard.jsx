// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/app/app/courses/components/CourseCard.jsx
// Individual course card component for displaying course information
// Extracted from massive CoursesPage component for better maintainability  
// RELEVANT FILES: CoursesData.js, CourseGrid.jsx, CoursesPage.jsx, CourseFilters.jsx

'use client';

import React, { memo } from 'react';
import { motion } from 'framer-motion';
import { 
  GraduationCap, 
  Star,
  Clock,
  Users,
  Play,
  BookOpen,
  Heart,
  Share2,
  CheckCircle
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { getCategoryColor, getLevelColor, categories } from '../data/CoursesData';
import { createAriaProps, generateId } from '@/utils/accessibility';

const CourseCard = ({ course, featured = false }) => {
  const cardId = `course-${course.id}`;
  const titleId = `${cardId}-title`;
  const descId = `${cardId}-description`;
  
  const ariaLabel = `${course.title} by ${course.instructor}. ${course.level} level course. ${course.rating} stars. ${course.students.toLocaleString()} students enrolled. ${course.isEnrolled ? 'You are enrolled in this course.' : 'Click to enroll.'}`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      className="group"
    >
      <Card 
        className={`overflow-hidden hover:shadow-xl transition-all duration-300 ${featured ? 'border-2 border-blue-200' : ''}`}
        role="article"
        aria-labelledby={titleId}
        aria-describedby={descId}
        tabIndex={0}
        {...createAriaProps(ariaLabel)}
      >
      <div className="relative">
        <div className="aspect-video bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
          <GraduationCap className="h-16 w-16 text-white opacity-50" />
        </div>
        
        {/* Course Status Badges */}
        <div className="absolute top-3 left-3 flex space-x-2">
          {course.isEnrolled && (
            <Badge className="bg-green-600 text-white">
              <CheckCircle className="h-3 w-3 mr-1" />
              Enrolled
            </Badge>
          )}
          {featured && (
            <Badge className="bg-yellow-600 text-white">
              <Star className="h-3 w-3 mr-1" />
              Featured
            </Badge>
          )}
        </div>
        
        {/* Action Buttons */}
        <div className="absolute top-3 right-3 flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button
            variant="secondary"
            size="sm"
            className="h-8 w-8 p-0 bg-white/90"
            onClick={(e) => e.stopPropagation()}
          >
            <Heart className={`h-4 w-4 ${course.isFavorite ? 'fill-red-500 text-red-500' : ''}`} />
          </Button>
          <Button
            variant="secondary"
            size="sm"
            className="h-8 w-8 p-0 bg-white/90"
            onClick={(e) => e.stopPropagation()}
          >
            <Share2 className="h-4 w-4" />
          </Button>
        </div>

        {/* Progress Bar for Enrolled Courses */}
        {course.isEnrolled && course.progress > 0 && (
          <div className="absolute bottom-0 left-0 right-0 bg-black/50 p-2">
            <div className="flex items-center justify-between text-white text-xs mb-1">
              <span>Progress</span>
              <span>{course.progress}%</span>
            </div>
            <Progress value={course.progress} className="h-1" />
          </div>
        )}
      </div>

      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <Badge className={getCategoryColor(course.category)}>
                {categories.find(c => c.id === course.category)?.name}
              </Badge>
              <Badge className={getLevelColor(course.level)}>
                {course.level}
              </Badge>
            </div>
            <h3 
              id={titleId}
              className="font-semibold text-lg leading-tight group-hover:text-blue-600 transition-colors"
            >
              {course.title}
            </h3>
          </div>
        </div>

        {/* Instructor */}
        <div className="flex items-center space-x-2 mb-3">
          <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center">
            <span className="text-xs font-medium">{course.instructor.charAt(0)}</span>
          </div>
          <span className="text-sm text-gray-600">{course.instructor}</span>
        </div>

        {/* Description */}
        <p 
          id={descId}
          className="text-gray-600 text-sm mb-4 line-clamp-2"
        >
          {course.description}
        </p>

        {/* Stats */}
        <div className="flex items-center space-x-4 text-xs text-gray-500 mb-4">
          <span className="flex items-center space-x-1">
            <Clock className="h-3 w-3" />
            <span>{course.duration}</span>
          </span>
          <span className="flex items-center space-x-1">
            <BookOpen className="h-3 w-3" />
            <span>{course.lessons} lessons</span>
          </span>
          <span className="flex items-center space-x-1">
            <Users className="h-3 w-3" />
            <span>{course.students.toLocaleString()}</span>
          </span>
        </div>

        {/* Rating */}
        <div className="flex items-center space-x-2 mb-4">
          <div className="flex items-center">
            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
            <span className="text-sm font-medium ml-1">{course.rating}</span>
          </div>
          <span className="text-xs text-gray-500">({course.reviews.toLocaleString()} reviews)</span>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mb-4">
          {course.tags.slice(0, 3).map(tag => (
            <Badge key={tag} variant="outline" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-lg font-bold text-gray-900">{course.price}</span>
            <span className="text-sm text-gray-500 line-through">{course.originalPrice}</span>
          </div>
          
          <Button 
            className={`${
              course.isEnrolled 
                ? 'bg-green-600 hover:bg-green-700' 
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {course.isEnrolled ? (
              <>
                <Play className="h-4 w-4 mr-2" />
                Continue
              </>
            ) : (
              <>
                <BookOpen className="h-4 w-4 mr-2" />
                Enroll Now
              </>
            )}
          </Button>
        </div>
      </div>
    </Card>
  </motion.div>
  );
};

// Memoize component to prevent unnecessary re-renders
export default memo(CourseCard);