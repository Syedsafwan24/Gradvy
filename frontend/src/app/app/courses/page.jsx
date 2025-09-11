'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  GraduationCap, 
  Search, 
  Filter,
  Star,
  Clock,
  Users,
  Play,
  BookOpen,
  Award,
  TrendingUp,
  Calendar,
  ChevronRight,
  Heart,
  Share2,
  Bookmark,
  CheckCircle
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

const CoursesPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedLevel, setSelectedLevel] = useState('all');
  const [sortBy, setSortBy] = useState('popular');
  const [viewMode, setViewMode] = useState('grid');

  const categories = [
    { id: 'all', name: 'All Courses', count: 234 },
    { id: 'programming', name: 'Programming', count: 52 },
    { id: 'web-development', name: 'Web Development', count: 38 },
    { id: 'data-science', name: 'Data Science', count: 35 },
    { id: 'ai-ml', name: 'AI & Machine Learning', count: 28 },
    { id: 'cloud-computing', name: 'Cloud Computing', count: 24 },
    { id: 'mobile-development', name: 'Mobile Development', count: 22 },
    { id: 'cybersecurity', name: 'Cybersecurity', count: 18 },
    { id: 'devops', name: 'DevOps', count: 15 },
    { id: 'product-management', name: 'Product Management', count: 14 },
    { id: 'design', name: 'Design', count: 12 },
    { id: 'blockchain', name: 'Blockchain & Web3', count: 8 }
  ];

  const courses = [
    {
      id: 1,
      title: 'Complete React Developer Course',
      instructor: 'Sarah Chen',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Master React from fundamentals to advanced concepts including hooks, context, and testing.',
      thumbnail: '/api/placeholder/300/200',
      category: 'web-development',
      level: 'intermediate',
      duration: '40 hours',
      lessons: 156,
      students: 12500,
      rating: 4.8,
      reviews: 2100,
      price: '$89.99',
      originalPrice: '$159.99',
      tags: ['React', 'JavaScript', 'Frontend'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-15',
      certificateAvailable: true
    },
    {
      id: 2,
      title: 'Python for Data Science Masterclass',
      instructor: 'Dr. Michael Rodriguez',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Learn Python programming for data analysis, visualization, and machine learning.',
      thumbnail: '/api/placeholder/300/200',
      category: 'data-science',
      level: 'beginner',
      duration: '35 hours',
      lessons: 128,
      students: 8900,
      rating: 4.9,
      reviews: 1650,
      price: '$79.99',
      originalPrice: '$139.99',
      tags: ['Python', 'Data Science', 'Machine Learning'],
      isEnrolled: true,
      isFavorite: true,
      progress: 45,
      lastUpdated: '2024-01-20',
      certificateAvailable: true
    },
    {
      id: 3,
      title: 'Full Stack JavaScript Development',
      instructor: 'Alex Thompson',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Build complete web applications using Node.js, Express, MongoDB, and React.',
      thumbnail: '/api/placeholder/300/200',
      category: 'web-development',
      level: 'advanced',
      duration: '60 hours',
      lessons: 220,
      students: 15600,
      rating: 4.7,
      reviews: 2800,
      price: '$119.99',
      originalPrice: '$199.99',
      tags: ['JavaScript', 'Node.js', 'Full Stack'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-10',
      certificateAvailable: true
    },
    {
      id: 4,
      title: 'Mobile App Development with React Native',
      instructor: 'Emma Wilson',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Create cross-platform mobile applications using React Native and modern tools.',
      thumbnail: '/api/placeholder/300/200',
      category: 'mobile-development',
      level: 'intermediate',
      duration: '45 hours',
      lessons: 180,
      students: 7200,
      rating: 4.6,
      reviews: 890,
      price: '$99.99',
      originalPrice: '$169.99',
      tags: ['React Native', 'Mobile', 'JavaScript'],
      isEnrolled: false,
      isFavorite: true,
      progress: 0,
      lastUpdated: '2024-01-18',
      certificateAvailable: true
    },
    {
      id: 5,
      title: 'DevOps Fundamentals with Docker & Kubernetes',
      instructor: 'David Kim',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Master containerization, orchestration, and CI/CD pipelines for modern development.',
      thumbnail: '/api/placeholder/300/200',
      category: 'devops',
      level: 'intermediate',
      duration: '30 hours',
      lessons: 95,
      students: 5400,
      rating: 4.8,
      reviews: 720,
      price: '$89.99',
      originalPrice: '$149.99',
      tags: ['Docker', 'Kubernetes', 'DevOps'],
      isEnrolled: true,
      isFavorite: false,
      progress: 20,
      lastUpdated: '2024-01-12',
      certificateAvailable: true
    },
    {
      id: 6,
      title: 'UI/UX Design Principles and Practice',
      instructor: 'Lisa Garcia',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Learn user interface and experience design from concept to implementation.',
      thumbnail: '/api/placeholder/300/200',
      category: 'design',
      level: 'beginner',
      duration: '25 hours',
      lessons: 75,
      students: 3200,
      rating: 4.7,
      reviews: 450,
      price: '$69.99',
      originalPrice: '$119.99',
      tags: ['UI/UX', 'Design', 'Figma'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-22',
      certificateAvailable: true
    },
    // AI & Machine Learning Courses
    {
      id: 7,
      title: 'Deep Learning with TensorFlow and Keras',
      instructor: 'Dr. Priya Sharma',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Master deep learning concepts and build neural networks from scratch using TensorFlow 2.0 and Keras.',
      thumbnail: '/api/placeholder/300/200',
      category: 'ai-ml',
      level: 'advanced',
      duration: '55 hours',
      lessons: 185,
      students: 9800,
      rating: 4.9,
      reviews: 1420,
      price: '$129.99',
      originalPrice: '$199.99',
      tags: ['TensorFlow', 'Deep Learning', 'Neural Networks'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-25',
      certificateAvailable: true
    },
    {
      id: 8,
      title: 'Machine Learning A-Z: Complete ML with Python',
      instructor: 'Prof. Andrew Martinez',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Comprehensive machine learning course covering supervised, unsupervised, and reinforcement learning.',
      thumbnail: '/api/placeholder/300/200',
      category: 'ai-ml',
      level: 'intermediate',
      duration: '42 hours',
      lessons: 165,
      students: 18500,
      rating: 4.8,
      reviews: 3200,
      price: '$99.99',
      originalPrice: '$179.99',
      tags: ['Machine Learning', 'Python', 'Scikit-learn'],
      isEnrolled: true,
      isFavorite: true,
      progress: 25,
      lastUpdated: '2024-01-20',
      certificateAvailable: true
    },
    {
      id: 9,
      title: 'Computer Vision Masterclass with OpenCV',
      instructor: 'Dr. Jennifer Liu',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Learn computer vision techniques, image processing, and object detection using OpenCV and Python.',
      thumbnail: '/api/placeholder/300/200',
      category: 'ai-ml',
      level: 'advanced',
      duration: '38 hours',
      lessons: 142,
      students: 6700,
      rating: 4.7,
      reviews: 890,
      price: '$119.99',
      originalPrice: '$189.99',
      tags: ['Computer Vision', 'OpenCV', 'Image Processing'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-18',
      certificateAvailable: true
    },
    // Cloud Computing Courses
    {
      id: 10,
      title: 'AWS Solutions Architect Associate 2024',
      instructor: 'Ryan Cooper',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Complete AWS certification course covering all services needed for the Solutions Architect exam.',
      thumbnail: '/api/placeholder/300/200',
      category: 'cloud-computing',
      level: 'intermediate',
      duration: '65 hours',
      lessons: 245,
      students: 22400,
      rating: 4.8,
      reviews: 4100,
      price: '$149.99',
      originalPrice: '$249.99',
      tags: ['AWS', 'Cloud Architecture', 'Certification'],
      isEnrolled: false,
      isFavorite: true,
      progress: 0,
      lastUpdated: '2024-01-28',
      certificateAvailable: true
    },
    {
      id: 11,
      title: 'Microsoft Azure Fundamentals AZ-900',
      instructor: 'Maria Gonzalez',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Learn Azure cloud services, pricing, and support. Perfect preparation for AZ-900 certification.',
      thumbnail: '/api/placeholder/300/200',
      category: 'cloud-computing',
      level: 'beginner',
      duration: '28 hours',
      lessons: 95,
      students: 14200,
      rating: 4.6,
      reviews: 1850,
      price: '$79.99',
      originalPrice: '$129.99',
      tags: ['Azure', 'Cloud Fundamentals', 'Microsoft'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-24',
      certificateAvailable: true
    },
    {
      id: 12,
      title: 'Google Cloud Professional Cloud Architect',
      instructor: 'James Chen',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Master Google Cloud Platform services and prepare for the Professional Cloud Architect certification.',
      thumbnail: '/api/placeholder/300/200',
      category: 'cloud-computing',
      level: 'advanced',
      duration: '48 hours',
      lessons: 178,
      students: 8900,
      rating: 4.7,
      reviews: 1240,
      price: '$139.99',
      originalPrice: '$219.99',
      tags: ['Google Cloud', 'GCP', 'Cloud Architecture'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-22',
      certificateAvailable: true
    },
    // Cybersecurity Courses
    {
      id: 13,
      title: 'Ethical Hacking and Penetration Testing',
      instructor: 'Marcus Johnson',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Learn ethical hacking techniques, penetration testing methodologies, and security assessment.',
      thumbnail: '/api/placeholder/300/200',
      category: 'cybersecurity',
      level: 'intermediate',
      duration: '52 hours',
      lessons: 198,
      students: 11400,
      rating: 4.8,
      reviews: 1680,
      price: '$129.99',
      originalPrice: '$199.99',
      tags: ['Ethical Hacking', 'Penetration Testing', 'Cybersecurity'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-26',
      certificateAvailable: true
    },
    {
      id: 14,
      title: 'Cybersecurity Fundamentals for Beginners',
      instructor: 'Dr. Angela White',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Comprehensive introduction to cybersecurity concepts, threats, and defense strategies.',
      thumbnail: '/api/placeholder/300/200',
      category: 'cybersecurity',
      level: 'beginner',
      duration: '32 hours',
      lessons: 115,
      students: 9600,
      rating: 4.7,
      reviews: 1320,
      price: '$89.99',
      originalPrice: '$149.99',
      tags: ['Cybersecurity', 'Network Security', 'InfoSec'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-20',
      certificateAvailable: true
    },
    // Product Management Courses
    {
      id: 15,
      title: 'Product Management Masterclass 2024',
      instructor: 'Sarah Rodriguez',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Complete product management course covering strategy, roadmaps, user research, and metrics.',
      thumbnail: '/api/placeholder/300/200',
      category: 'product-management',
      level: 'intermediate',
      duration: '45 hours',
      lessons: 168,
      students: 7800,
      rating: 4.9,
      reviews: 1150,
      price: '$119.99',
      originalPrice: '$189.99',
      tags: ['Product Management', 'Strategy', 'User Research'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-27',
      certificateAvailable: true
    },
    {
      id: 16,
      title: 'Agile Product Owner Certification Prep',
      instructor: 'Michael Turner',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Master Agile methodologies, Scrum framework, and Product Owner responsibilities.',
      thumbnail: '/api/placeholder/300/200',
      category: 'product-management',
      level: 'beginner',
      duration: '28 hours',
      lessons: 92,
      students: 5400,
      rating: 4.6,
      reviews: 780,
      price: '$99.99',
      originalPrice: '$159.99',
      tags: ['Agile', 'Scrum', 'Product Owner'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-23',
      certificateAvailable: true
    },
    // Advanced Programming Courses
    {
      id: 17,
      title: 'System Design Interview Preparation',
      instructor: 'Dr. Kevin Park',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Master system design concepts for technical interviews at top tech companies.',
      thumbnail: '/api/placeholder/300/200',
      category: 'programming',
      level: 'advanced',
      duration: '40 hours',
      lessons: 125,
      students: 13600,
      rating: 4.9,
      reviews: 2100,
      price: '$139.99',
      originalPrice: '$219.99',
      tags: ['System Design', 'Interviews', 'Scalability'],
      isEnrolled: true,
      isFavorite: true,
      progress: 65,
      lastUpdated: '2024-01-29',
      certificateAvailable: true
    },
    {
      id: 18,
      title: 'Advanced Data Structures and Algorithms',
      instructor: 'Prof. Lisa Zhang',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Deep dive into advanced algorithms, data structures, and problem-solving techniques.',
      thumbnail: '/api/placeholder/300/200',
      category: 'programming',
      level: 'advanced',
      duration: '58 hours',
      lessons: 215,
      students: 10800,
      rating: 4.8,
      reviews: 1650,
      price: '$129.99',
      originalPrice: '$199.99',
      tags: ['Algorithms', 'Data Structures', 'Problem Solving'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-25',
      certificateAvailable: true
    },
    {
      id: 19,
      title: 'Microservices Architecture with Spring Boot',
      instructor: 'Robert Davis',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Build scalable microservices using Spring Boot, Docker, and Kubernetes.',
      thumbnail: '/api/placeholder/300/200',
      category: 'programming',
      level: 'advanced',
      duration: '42 hours',
      lessons: 156,
      students: 8200,
      rating: 4.7,
      reviews: 980,
      price: '$119.99',
      originalPrice: '$179.99',
      tags: ['Microservices', 'Spring Boot', 'Java'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-21',
      certificateAvailable: true
    },
    // Blockchain & Web3 Courses
    {
      id: 20,
      title: 'Blockchain Development with Solidity',
      instructor: 'Alex Cryptocurrency',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Learn blockchain development, smart contracts, and DApp creation using Solidity.',
      thumbnail: '/api/placeholder/300/200',
      category: 'blockchain',
      level: 'intermediate',
      duration: '35 hours',
      lessons: 128,
      students: 4600,
      rating: 4.6,
      reviews: 620,
      price: '$149.99',
      originalPrice: '$229.99',
      tags: ['Blockchain', 'Solidity', 'Smart Contracts'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-30',
      certificateAvailable: true
    },
    {
      id: 21,
      title: 'Web3 Development Complete Guide',
      instructor: 'Maya Decentralized',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Build decentralized applications (DApps) using Web3.js, React, and Ethereum.',
      thumbnail: '/api/placeholder/300/200',
      category: 'blockchain',
      level: 'intermediate',
      duration: '38 hours',
      lessons: 142,
      students: 3800,
      rating: 4.5,
      reviews: 445,
      price: '$139.99',
      originalPrice: '$209.99',
      tags: ['Web3', 'DApps', 'Ethereum'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-28',
      certificateAvailable: true
    },
    // Additional Data Science Courses
    {
      id: 22,
      title: 'Advanced Statistics for Data Science',
      instructor: 'Dr. Rachel Kim',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Master statistical concepts essential for data science and machine learning.',
      thumbnail: '/api/placeholder/300/200',
      category: 'data-science',
      level: 'intermediate',
      duration: '32 hours',
      lessons: 118,
      students: 7200,
      rating: 4.8,
      reviews: 1050,
      price: '$89.99',
      originalPrice: '$149.99',
      tags: ['Statistics', 'Data Science', 'Analytics'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-24',
      certificateAvailable: true
    },
    {
      id: 23,
      title: 'Big Data Analytics with Apache Spark',
      instructor: 'Daniel Hadoop',
      instructorAvatar: '/api/placeholder/40/40',
      description: 'Process and analyze big data using Apache Spark, Scala, and distributed computing.',
      thumbnail: '/api/placeholder/300/200',
      category: 'data-science',
      level: 'advanced',
      duration: '46 hours',
      lessons: 172,
      students: 5900,
      rating: 4.7,
      reviews: 780,
      price: '$129.99',
      originalPrice: '$199.99',
      tags: ['Big Data', 'Apache Spark', 'Scala'],
      isEnrolled: false,
      isFavorite: false,
      progress: 0,
      lastUpdated: '2024-01-26',
      certificateAvailable: true
    }
  ];

  const featuredCourses = courses.slice(0, 3);
  const enrolledCourses = courses.filter(course => course.isEnrolled);
  
  const getLevelColor = (level) => {
    switch (level) {
      case 'beginner': return 'bg-green-100 text-green-700';
      case 'intermediate': return 'bg-yellow-100 text-yellow-700';
      case 'advanced': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'programming': 'bg-blue-100 text-blue-700',
      'web-development': 'bg-green-100 text-green-700',
      'data-science': 'bg-purple-100 text-purple-700',
      'ai-ml': 'bg-violet-100 text-violet-700',
      'cloud-computing': 'bg-sky-100 text-sky-700',
      'mobile-development': 'bg-orange-100 text-orange-700',
      'cybersecurity': 'bg-red-100 text-red-700',
      'devops': 'bg-indigo-100 text-indigo-700',
      'product-management': 'bg-emerald-100 text-emerald-700',
      'design': 'bg-pink-100 text-pink-700',
      'blockchain': 'bg-yellow-100 text-yellow-700'
    };
    return colors[category] || 'bg-gray-100 text-gray-700';
  };

  const CourseCard = ({ course, featured = false }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      className="group"
    >
      <Card className={`overflow-hidden hover:shadow-xl transition-all duration-300 ${featured ? 'border-2 border-blue-200' : ''}`}>
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
              <h3 className="font-semibold text-lg leading-tight group-hover:text-blue-600 transition-colors">
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
          <p className="text-gray-600 text-sm mb-4 line-clamp-2">
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

  const filteredCourses = courses.filter(course => {
    const matchesSearch = course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          course.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          course.instructor.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || course.category === selectedCategory;
    const matchesLevel = selectedLevel === 'all' || course.level === selectedLevel;
    
    return matchesSearch && matchesCategory && matchesLevel;
  });

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
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-col lg:flex-row gap-4"
        >
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search courses, instructors, or topics..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="lg:w-48">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              {categories.map(category => (
                <SelectItem key={category.id} value={category.id}>
                  {category.name} ({category.count})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={selectedLevel} onValueChange={setSelectedLevel}>
            <SelectTrigger className="lg:w-48">
              <SelectValue placeholder="Level" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Levels</SelectItem>
              <SelectItem value="beginner">Beginner</SelectItem>
              <SelectItem value="intermediate">Intermediate</SelectItem>
              <SelectItem value="advanced">Advanced</SelectItem>
            </SelectContent>
          </Select>

          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="lg:w-48">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="popular">Most Popular</SelectItem>
              <SelectItem value="newest">Newest First</SelectItem>
              <SelectItem value="rating">Highest Rated</SelectItem>
              <SelectItem value="price-low">Price: Low to High</SelectItem>
              <SelectItem value="price-high">Price: High to Low</SelectItem>
            </SelectContent>
          </Select>
        </motion.div>

        {/* Main Content */}
        <Tabs defaultValue="all-courses">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all-courses">All Courses</TabsTrigger>
            <TabsTrigger value="featured">Featured</TabsTrigger>
            <TabsTrigger value="enrolled">My Courses</TabsTrigger>
            <TabsTrigger value="favorites">Favorites</TabsTrigger>
          </TabsList>

          <TabsContent value="all-courses" className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {filteredCourses.map(course => (
                <CourseCard key={course.id} course={course} />
              ))}
            </motion.div>
          </TabsContent>

          <TabsContent value="featured" className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {featuredCourses.map(course => (
                <CourseCard key={course.id} course={course} featured />
              ))}
            </motion.div>
          </TabsContent>

          <TabsContent value="enrolled" className="mt-6">
            {enrolledCourses.length === 0 ? (
              <Card className="p-12 text-center">
                <BookOpen className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Enrolled Courses</h3>
                <p className="text-gray-600 mb-6">Start learning by enrolling in your first course.</p>
                <Button>Browse Courses</Button>
              </Card>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
              >
                {enrolledCourses.map(course => (
                  <CourseCard key={course.id} course={course} />
                ))}
              </motion.div>
            )}
          </TabsContent>

          <TabsContent value="favorites" className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {courses.filter(course => course.isFavorite).map(course => (
                <CourseCard key={course.id} course={course} />
              ))}
            </motion.div>
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