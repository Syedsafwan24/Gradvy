// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/app/app/courses/components/CourseGrid.jsx
// Grid layout component for displaying course cards
// Extracted from massive CoursesPage component for better maintainability
// RELEVANT FILES: CourseCard.jsx, CoursesData.js, CoursesPage.jsx, CourseFilters.jsx

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import CourseCard from './CourseCard';

const CourseGrid = ({ courses, featured = false, emptyStateTitle, emptyStateDescription }) => {
  if (courses.length === 0) {
    return (
      <Card className="p-12 text-center">
        <BookOpen className="h-16 w-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {emptyStateTitle || 'No Courses Found'}
        </h3>
        <p className="text-gray-600 mb-6">
          {emptyStateDescription || 'Try adjusting your search criteria or explore other courses.'}
        </p>
        <Button>Browse All Courses</Button>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.2 }}
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      {courses.map(course => (
        <CourseCard key={course.id} course={course} featured={featured} />
      ))}
    </motion.div>
  );
};

export default CourseGrid;