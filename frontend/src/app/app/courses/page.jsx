// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/app/app/courses/page.jsx
// Main courses page with course browsing, filtering, and enrollment functionality
// Refactored from massive 947-line component into focused modular components
// RELEVANT FILES: CourseCard.jsx, CourseFilters.jsx, CourseGrid.jsx, CoursesData.js

'use client';

import React, { useState, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { GraduationCap, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { courses, getFeaturedCourses, getEnrolledCourses, filterCourses } from './data/CoursesData';
import CourseFilters from './components/CourseFilters';
import CourseGrid from './components/CourseGrid';

const CoursesPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedLevel, setSelectedLevel] = useState('all');
  const [sortBy, setSortBy] = useState('popular');

  // Memoize expensive computations to prevent unnecessary recalculations
  const featuredCourses = useMemo(() => getFeaturedCourses(), []);
  const enrolledCourses = useMemo(() => getEnrolledCourses(), []);
  const favoriteCourses = useMemo(() => courses.filter(course => course.isFavorite), []);
  
  const filteredCourses = useMemo(() => 
    filterCourses(courses, { searchTerm, selectedCategory, selectedLevel }),
    [searchTerm, selectedCategory, selectedLevel]
  );

  // Memoize filter handlers to prevent CourseFilters re-renders
  const handleSearchChange = useCallback((value) => setSearchTerm(value), []);
  const handleCategoryChange = useCallback((value) => setSelectedCategory(value), []);
  const handleLevelChange = useCallback((value) => setSelectedLevel(value), []);
  const handleSortChange = useCallback((value) => setSortBy(value), []);

  return (
    <ProtectedRoute>
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg"
        >
          <GraduationCap className="h-16 w-16 text-blue-600 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Course Catalog</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Discover and enroll in high-quality courses designed to accelerate your learning journey.
            From beginner tutorials to advanced masterclasses.
          </p>
        </motion.div>

        {/* Search and Filters */}
        <CourseFilters
          searchTerm={searchTerm}
          setSearchTerm={handleSearchChange}
          selectedCategory={selectedCategory}
          setSelectedCategory={handleCategoryChange}
          selectedLevel={selectedLevel}
          setSelectedLevel={handleLevelChange}
          sortBy={sortBy}
          setSortBy={handleSortChange}
        />

        {/* Main Content */}
        <Tabs defaultValue="all-courses">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all-courses">All Courses</TabsTrigger>
            <TabsTrigger value="featured">Featured</TabsTrigger>
            <TabsTrigger value="enrolled">My Courses</TabsTrigger>
            <TabsTrigger value="favorites">Favorites</TabsTrigger>
          </TabsList>

          <TabsContent value="all-courses" className="mt-6">
            <CourseGrid courses={filteredCourses} />
          </TabsContent>

          <TabsContent value="featured" className="mt-6">
            <CourseGrid courses={featuredCourses} featured />
          </TabsContent>

          <TabsContent value="enrolled" className="mt-6">
            <CourseGrid 
              courses={enrolledCourses} 
              emptyStateTitle="No Enrolled Courses"
              emptyStateDescription="Start learning by enrolling in your first course."
            />
          </TabsContent>

          <TabsContent value="favorites" className="mt-6">
            <CourseGrid 
              courses={favoriteCourses} 
              emptyStateTitle="No Favorite Courses"
              emptyStateDescription="Mark courses as favorites to see them here."
            />
          </TabsContent>
        </Tabs>

        {/* Load More */}
        {filteredCourses.length > 0 && (
          <div className="text-center">
            <Button variant="outline" size="lg">
              Load More Courses
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
};

export default CoursesPage;