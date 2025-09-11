'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BookOpen, 
  Play, 
  Clock,
  Star,
  TrendingUp,
  Award,
  Target,
  Calendar,
  CheckCircle,
  BarChart3,
  Users,
  Flame,
  ChevronRight,
  Filter,
  Search,
  Plus
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import Link from 'next/link';

const LearningPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPath, setSelectedPath] = useState('all');

  const learningStats = {
    currentStreak: 15,
    totalHours: 127,
    coursesCompleted: 8,
    skillsLearned: 12,
    currentLevel: 'Intermediate',
    pointsEarned: 2750,
    nextMilestone: 3000
  };

  const currentCourses = [
    {
      id: 1,
      title: 'Advanced React Patterns',
      instructor: 'Sarah Chen',
      progress: 68,
      totalLessons: 45,
      completedLessons: 31,
      estimatedTime: '2.5 hours left',
      difficulty: 'Advanced',
      category: 'Frontend',
      lastAccessed: '2 hours ago',
      thumbnail: '/api/placeholder/300/200',
      nextLesson: 'Custom Hooks and Context Patterns'
    },
    {
      id: 2,
      title: 'Python Data Science Fundamentals',
      instructor: 'Dr. Michael Rodriguez',
      progress: 45,
      totalLessons: 60,
      completedLessons: 27,
      estimatedTime: '4.2 hours left',
      difficulty: 'Intermediate',
      category: 'Data Science',
      lastAccessed: '1 day ago',
      thumbnail: '/api/placeholder/300/200',
      nextLesson: 'Data Visualization with Matplotlib'
    },
    {
      id: 3,
      title: 'DevOps with Docker & Kubernetes',
      instructor: 'David Kim',
      progress: 25,
      totalLessons: 38,
      completedLessons: 9,
      estimatedTime: '6.8 hours left',
      difficulty: 'Advanced',
      category: 'DevOps',
      lastAccessed: '3 days ago',
      thumbnail: '/api/placeholder/300/200',
      nextLesson: 'Container Orchestration Basics'
    }
  ];

  const learningPaths = [
    {
      id: 1,
      title: 'Full Stack Web Development',
      description: 'Master frontend and backend development with modern technologies',
      progress: 45,
      courses: 8,
      completedCourses: 4,
      estimatedDuration: '6 months',
      difficulty: 'Intermediate',
      skills: ['React', 'Node.js', 'MongoDB', 'Express'],
      isActive: true
    },
    {
      id: 2,
      title: 'Data Science & Machine Learning',
      description: 'Learn data analysis, visualization, and machine learning algorithms',
      progress: 30,
      courses: 10,
      completedCourses: 3,
      estimatedDuration: '8 months',
      difficulty: 'Advanced',
      skills: ['Python', 'Pandas', 'Scikit-learn', 'TensorFlow'],
      isActive: false
    },
    {
      id: 3,
      title: 'Mobile App Development',
      description: 'Build cross-platform mobile applications with React Native',
      progress: 15,
      courses: 6,
      completedCourses: 1,
      estimatedDuration: '4 months',
      difficulty: 'Intermediate',
      skills: ['React Native', 'JavaScript', 'Mobile UI/UX'],
      isActive: false
    }
  ];

  const recentActivity = [
    {
      type: 'completed_lesson',
      title: 'Completed "State Management with Redux"',
      course: 'Advanced React Patterns',
      time: '2 hours ago',
      points: 50
    },
    {
      type: 'achievement',
      title: 'Earned "React Master" badge',
      course: 'React Learning Path',
      time: '1 day ago',
      points: 100
    },
    {
      type: 'streak',
      title: 'Maintained 15-day learning streak',
      course: null,
      time: '1 day ago',
      points: 25
    },
    {
      type: 'completed_course',
      title: 'Completed "JavaScript ES6+ Features"',
      course: 'JavaScript Mastery',
      time: '3 days ago',
      points: 200
    }
  ];

  const recommendedCourses = [
    {
      id: 1,
      title: 'TypeScript for React Developers',
      instructor: 'Emma Wilson',
      rating: 4.8,
      students: 12500,
      duration: '6.5 hours',
      price: '$49.99',
      difficulty: 'Intermediate',
      match: 95
    },
    {
      id: 2,
      title: 'Next.js Production Applications',
      instructor: 'Alex Thompson',
      rating: 4.9,
      students: 8900,
      duration: '8.2 hours',
      price: '$79.99',
      difficulty: 'Advanced',
      match: 92
    },
    {
      id: 3,
      title: 'GraphQL API Development',
      instructor: 'Lisa Garcia',
      rating: 4.7,
      students: 6200,
      duration: '5.5 hours',
      price: '$59.99',
      difficulty: 'Intermediate',
      match: 88
    }
  ];

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Beginner': return 'bg-green-100 text-green-700';
      case 'Intermediate': return 'bg-yellow-100 text-yellow-700';
      case 'Advanced': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'completed_lesson': return CheckCircle;
      case 'achievement': return Award;
      case 'streak': return Flame;
      case 'completed_course': return BookOpen;
      default: return BookOpen;
    }
  };

  const CurrentCourseCard = ({ course }) => (
    <Card className="overflow-hidden hover:shadow-lg transition-all duration-300 group">
      <div className="relative">
        <div className="aspect-video bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
          <BookOpen className="h-12 w-12 text-white opacity-50" />
        </div>
        <div className="absolute bottom-0 left-0 right-0 bg-black/50 p-3">
          <div className="flex items-center justify-between text-white text-sm mb-2">
            <span>Progress: {course.progress}%</span>
            <span>{course.completedLessons}/{course.totalLessons} lessons</span>
          </div>
          <Progress value={course.progress} className="h-2" />
        </div>
      </div>
      
      <div className="p-6">
        <div className="flex items-center justify-between mb-3">
          <Badge className={getDifficultyColor(course.difficulty)}>
            {course.difficulty}
          </Badge>
          <Badge variant="outline">{course.category}</Badge>
        </div>
        
        <h3 className="font-semibold text-lg mb-2 group-hover:text-blue-600 transition-colors">
          {course.title}
        </h3>
        
        <p className="text-gray-600 text-sm mb-3">by {course.instructor}</p>
        
        <div className="flex items-center space-x-4 text-xs text-gray-500 mb-4">
          <span className="flex items-center space-x-1">
            <Clock className="h-3 w-3" />
            <span>{course.estimatedTime}</span>
          </span>
          <span>Last: {course.lastAccessed}</span>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-3 mb-4">
          <p className="text-sm font-medium text-gray-900 mb-1">Next Lesson:</p>
          <p className="text-sm text-gray-700">{course.nextLesson}</p>
        </div>
        
        <Button className="w-full bg-blue-600 hover:bg-blue-700">
          <Play className="h-4 w-4 mr-2" />
          Continue Learning
        </Button>
      </div>
    </Card>
  );

  const LearningPathCard = ({ path }) => (
    <Card className={`p-6 hover:shadow-lg transition-all duration-300 ${path.isActive ? 'border-2 border-blue-500 bg-blue-50' : ''}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="font-semibold text-lg">{path.title}</h3>
            {path.isActive && (
              <Badge className="bg-blue-600 text-white">Active</Badge>
            )}
          </div>
          <p className="text-gray-600 text-sm mb-3">{path.description}</p>
        </div>
      </div>
      
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Progress</span>
          <span className="text-sm text-gray-600">{path.progress}%</span>
        </div>
        <Progress value={path.progress} className="h-2 mb-2" />
        <p className="text-xs text-gray-500">
          {path.completedCourses}/{path.courses} courses completed
        </p>
      </div>
      
      <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
        <span className="flex items-center space-x-1">
          <Calendar className="h-3 w-3" />
          <span>{path.estimatedDuration}</span>
        </span>
        <Badge className={getDifficultyColor(path.difficulty)}>
          {path.difficulty}
        </Badge>
      </div>
      
      <div className="flex flex-wrap gap-1 mb-4">
        {path.skills.slice(0, 3).map(skill => (
          <Badge key={skill} variant="outline" className="text-xs">
            {skill}
          </Badge>
        ))}
        {path.skills.length > 3 && (
          <Badge variant="outline" className="text-xs">
            +{path.skills.length - 3} more
          </Badge>
        )}
      </div>
      
      <div className="flex space-x-2">
        <Button variant="outline" className="flex-1">
          View Path
        </Button>
        <Button className={`flex-1 ${path.isActive ? 'bg-green-600 hover:bg-green-700' : 'bg-blue-600 hover:bg-blue-700'}`}>
          {path.isActive ? 'Continue' : 'Start Path'}
        </Button>
      </div>
    </Card>
  );

  return (
    <ProtectedRoute>
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0"
        >
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Learning Dashboard</h1>
            <p className="text-gray-600">
              Track your progress, continue courses, and discover new learning opportunities
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <Button variant="outline" asChild>
              <Link href="/app/courses">
                <Search className="h-4 w-4 mr-2" />
                Browse Courses
              </Link>
            </Button>
            <Button asChild>
              <Link href="/app/career">
                <Target className="h-4 w-4 mr-2" />
                Learning Paths
              </Link>
            </Button>
          </div>
        </motion.div>

        {/* Learning Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4"
        >
          <Card className="p-4 text-center">
            <Flame className="h-8 w-8 text-orange-500 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{learningStats.currentStreak}</div>
            <div className="text-xs text-gray-600">Day Streak</div>
          </Card>
          
          <Card className="p-4 text-center">
            <Clock className="h-8 w-8 text-blue-500 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{learningStats.totalHours}</div>
            <div className="text-xs text-gray-600">Hours Learned</div>
          </Card>
          
          <Card className="p-4 text-center">
            <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{learningStats.coursesCompleted}</div>
            <div className="text-xs text-gray-600">Completed</div>
          </Card>
          
          <Card className="p-4 text-center">
            <Star className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{learningStats.skillsLearned}</div>
            <div className="text-xs text-gray-600">Skills</div>
          </Card>
          
          <Card className="p-4 text-center">
            <TrendingUp className="h-8 w-8 text-purple-500 mx-auto mb-2" />
            <div className="text-lg font-bold text-gray-900">{learningStats.currentLevel}</div>
            <div className="text-xs text-gray-600">Level</div>
          </Card>
          
          <Card className="p-4 text-center">
            <Award className="h-8 w-8 text-indigo-500 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{learningStats.pointsEarned}</div>
            <div className="text-xs text-gray-600">Points</div>
          </Card>
          
          <Card className="p-4 text-center">
            <Target className="h-8 w-8 text-pink-500 mx-auto mb-2" />
            <div className="text-lg font-bold text-gray-900">{learningStats.nextMilestone - learningStats.pointsEarned}</div>
            <div className="text-xs text-gray-600">To Next Level</div>
          </Card>
        </motion.div>

        {/* Main Content */}
        <Tabs defaultValue="current" className="mt-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="current">Current Courses</TabsTrigger>
            <TabsTrigger value="paths">Learning Paths</TabsTrigger>
            <TabsTrigger value="activity">Recent Activity</TabsTrigger>
            <TabsTrigger value="recommended">Recommended</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="current" className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Continue Learning</h2>
                <p className="text-sm text-gray-600">{currentCourses.length} courses in progress</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {currentCourses.map(course => (
                  <CurrentCourseCard key={course.id} course={course} />
                ))}
              </div>
              
              <Card className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Ready for more?</h3>
                    <p className="text-gray-600 text-sm">
                      Discover new courses and expand your skillset
                    </p>
                  </div>
                  <Button asChild>
                    <Link href="/app/courses">
                      <Plus className="h-4 w-4 mr-2" />
                      Browse Courses
                    </Link>
                  </Button>
                </div>
              </Card>
            </motion.div>
          </TabsContent>

          <TabsContent value="paths" className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Learning Paths</h2>
                <Button variant="outline" asChild>
                  <Link href="/app/career">
                    <ChevronRight className="h-4 w-4 mr-2" />
                    Explore All Paths
                  </Link>
                </Button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {learningPaths.map(path => (
                  <LearningPathCard key={path.id} path={path} />
                ))}
              </div>
            </motion.div>
          </TabsContent>

          <TabsContent value="activity" className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <h2 className="text-xl font-semibold">Recent Activity</h2>
              
              <div className="space-y-4">
                {recentActivity.map((activity, index) => {
                  const Icon = getActivityIcon(activity.type);
                  return (
                    <Card key={index} className="p-4">
                      <div className="flex items-center space-x-4">
                        <div className="p-2 bg-blue-100 rounded-full">
                          <Icon className="h-5 w-5 text-blue-600" />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{activity.title}</p>
                          {activity.course && (
                            <p className="text-sm text-gray-600">in {activity.course}</p>
                          )}
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium text-green-600">+{activity.points} pts</p>
                          <p className="text-xs text-gray-500">{activity.time}</p>
                        </div>
                      </div>
                    </Card>
                  );
                })}
              </div>
            </motion.div>
          </TabsContent>

          <TabsContent value="recommended" className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <h2 className="text-xl font-semibold">Recommended for You</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {recommendedCourses.map(course => (
                  <Card key={course.id} className="overflow-hidden hover:shadow-lg transition-all duration-300">
                    <div className="aspect-video bg-gradient-to-br from-green-500 to-teal-600 flex items-center justify-center">
                      <BookOpen className="h-12 w-12 text-white opacity-50" />
                    </div>
                    
                    <div className="p-6">
                      <div className="flex items-center justify-between mb-3">
                        <Badge className="bg-green-100 text-green-700">
                          {course.match}% match
                        </Badge>
                        <Badge className={getDifficultyColor(course.difficulty)}>
                          {course.difficulty}
                        </Badge>
                      </div>
                      
                      <h3 className="font-semibold text-lg mb-2">{course.title}</h3>
                      <p className="text-gray-600 text-sm mb-3">by {course.instructor}</p>
                      
                      <div className="flex items-center space-x-4 text-xs text-gray-500 mb-4">
                        <span className="flex items-center space-x-1">
                          <Star className="h-3 w-3" />
                          <span>{course.rating}</span>
                        </span>
                        <span className="flex items-center space-x-1">
                          <Users className="h-3 w-3" />
                          <span>{course.students.toLocaleString()}</span>
                        </span>
                        <span className="flex items-center space-x-1">
                          <Clock className="h-3 w-3" />
                          <span>{course.duration}</span>
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-lg font-bold text-gray-900">{course.price}</span>
                        <Button size="sm">
                          <BookOpen className="h-4 w-4 mr-2" />
                          Enroll
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </motion.div>
          </TabsContent>

          <TabsContent value="analytics" className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <h2 className="text-xl font-semibold">Learning Analytics</h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="p-6">
                  <h3 className="font-semibold mb-4">Weekly Learning Time</h3>
                  <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                    <div className="text-center text-gray-500">
                      <BarChart3 className="h-12 w-12 mx-auto mb-2" />
                      <p>Analytics chart would go here</p>
                    </div>
                  </div>
                </Card>
                
                <Card className="p-6">
                  <h3 className="font-semibold mb-4">Skill Progress</h3>
                  <div className="space-y-4">
                    {['React', 'JavaScript', 'Python', 'Node.js'].map((skill, index) => (
                      <div key={skill}>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-medium">{skill}</span>
                          <span className="text-sm text-gray-600">{85 - index * 10}%</span>
                        </div>
                        <Progress value={85 - index * 10} className="h-2" />
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
              
              <Card className="p-6">
                <h3 className="font-semibold mb-4">Learning Goals</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <Target className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                    <p className="font-semibold">Complete 3 Courses</p>
                    <p className="text-sm text-gray-600">2/3 completed</p>
                    <Progress value={66} className="h-2 mt-2" />
                  </div>
                  
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <Flame className="h-8 w-8 text-green-600 mx-auto mb-2" />
                    <p className="font-semibold">30-Day Streak</p>
                    <p className="text-sm text-gray-600">15/30 days</p>
                    <Progress value={50} className="h-2 mt-2" />
                  </div>
                  
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <Award className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                    <p className="font-semibold">Earn 5 Badges</p>
                    <p className="text-sm text-gray-600">3/5 earned</p>
                    <Progress value={60} className="h-2 mt-2" />
                  </div>
                </div>
              </Card>
            </motion.div>
          </TabsContent>
        </Tabs>
      </div>
    </ProtectedRoute>
  );
};

export default LearningPage;