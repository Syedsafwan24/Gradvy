'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Briefcase, 
  TrendingUp, 
  Target, 
  Award, 
  BookOpen, 
  Users, 
  MapPin,
  Calendar,
  Star,
  ChevronRight,
  ExternalLink,
  Plus,
  Settings,
  BarChart3,
  FileText,
  Linkedin,
  Github,
  Globe
} from 'lucide-react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/slices/authSlice';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import CareerPathways from '@/components/career/CareerPathways';
import SkillsMatrix from '@/components/career/SkillsMatrix';
import MarketInsights from '@/components/career/MarketInsights';
import ResumeBuilder from '@/components/career/ResumeBuilder';
import GoalTracker from '@/components/career/GoalTracker';

const CareerPage = () => {
  const user = useSelector(selectCurrentUser);
  const [activeTab, setActiveTab] = useState('overview');
  const [careerData, setCareerData] = useState({
    currentRole: '',
    experience: 0,
    targetRole: '',
    skills: [],
    goals: [],
    achievements: [],
    recommendations: []
  });

  // Mock career data - in real app this would come from API
  useEffect(() => {
    setCareerData({
      currentRole: 'Software Developer',
      experience: 2.5,
      targetRole: 'Senior Full Stack Developer',
      skills: [
        { name: 'JavaScript', level: 85, category: 'Programming' },
        { name: 'React', level: 78, category: 'Frontend' },
        { name: 'Node.js', level: 72, category: 'Backend' },
        { name: 'Python', level: 65, category: 'Programming' },
        { name: 'SQL', level: 70, category: 'Database' },
        { name: 'Git', level: 80, category: 'Tools' },
        { name: 'AWS', level: 45, category: 'Cloud' },
        { name: 'Docker', level: 55, category: 'DevOps' }
      ],
      goals: [
        {
          id: 1,
          title: 'Complete AWS Certification',
          description: 'Get AWS Solutions Architect Associate certification',
          progress: 60,
          deadline: '2024-06-30',
          status: 'in_progress'
        },
        {
          id: 2,
          title: 'Build Portfolio Project',
          description: 'Create a full-stack application showcasing skills',
          progress: 85,
          deadline: '2024-04-15',
          status: 'in_progress'
        },
        {
          id: 3,
          title: 'Improve System Design Skills',
          description: 'Study system design patterns and architecture',
          progress: 30,
          deadline: '2024-07-31',
          status: 'in_progress'
        }
      ],
      achievements: [
        {
          id: 1,
          title: 'React Certification',
          issuer: 'Meta',
          date: '2024-01-15',
          type: 'certification'
        },
        {
          id: 2,
          title: 'Hackathon Winner',
          issuer: 'TechCorp',
          date: '2023-11-20',
          type: 'achievement'
        },
        {
          id: 3,
          title: 'JavaScript Expert',
          issuer: 'Gradvy',
          date: '2024-02-01',
          type: 'skill_badge'
        }
      ],
      recommendations: [
        {
          id: 1,
          type: 'course',
          title: 'Advanced System Design',
          description: 'Master system design for senior roles',
          priority: 'high'
        },
        {
          id: 2,
          type: 'skill',
          title: 'TypeScript Mastery',
          description: 'Enhance JavaScript skills with TypeScript',
          priority: 'medium'
        },
        {
          id: 3,
          type: 'certification',
          title: 'Kubernetes Certification',
          description: 'Learn container orchestration',
          priority: 'low'
        }
      ]
    });
  }, []);

  const getSkillCategoryColor = (category) => {
    const colors = {
      'Programming': 'bg-blue-100 text-blue-700',
      'Frontend': 'bg-green-100 text-green-700',
      'Backend': 'bg-purple-100 text-purple-700',
      'Database': 'bg-yellow-100 text-yellow-700',
      'Tools': 'bg-gray-100 text-gray-700',
      'Cloud': 'bg-indigo-100 text-indigo-700',
      'DevOps': 'bg-red-100 text-red-700'
    };
    return colors[category] || 'bg-gray-100 text-gray-700';
  };

  const getGoalStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'in_progress': return 'bg-blue-500';
      case 'planned': return 'bg-gray-400';
      default: return 'bg-gray-400';
    }
  };

  const skillsByCategory = careerData.skills.reduce((acc, skill) => {
    if (!acc[skill.category]) {
      acc[skill.category] = [];
    }
    acc[skill.category].push(skill);
    return acc;
  }, {});

  const overallSkillLevel = Math.round(
    careerData.skills.reduce((sum, skill) => sum + skill.level, 0) / careerData.skills.length
  );

  return (
    <ProtectedRoute>
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Briefcase className="h-6 w-6 text-indigo-600" />
              <h1 className="text-2xl font-bold text-gray-900">Career Development</h1>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
            <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700">
              <Plus className="h-4 w-4 mr-2" />
              Add Goal
            </Button>
          </div>
        </motion.div>

        {/* Career Overview Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4"
        >
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Current Role</p>
                <p className="text-lg font-semibold text-gray-900">
                  {careerData.currentRole || 'Not Set'}
                </p>
              </div>
              <Briefcase className="h-8 w-8 text-blue-500" />
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Experience</p>
                <p className="text-lg font-semibold text-gray-900">
                  {careerData.experience} years
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-500" />
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Skill Level</p>
                <p className="text-lg font-semibold text-gray-900">
                  {overallSkillLevel}%
                </p>
              </div>
              <Star className="h-8 w-8 text-yellow-500" />
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Goals</p>
                <p className="text-lg font-semibold text-gray-900">
                  {careerData.goals.filter(g => g.status === 'in_progress').length}
                </p>
              </div>
              <Target className="h-8 w-8 text-purple-500" />
            </div>
          </Card>
        </motion.div>

        {/* Main Content Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-6">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="pathways">Pathways</TabsTrigger>
              <TabsTrigger value="skills">Skills</TabsTrigger>
              <TabsTrigger value="goals">Goals</TabsTrigger>
              <TabsTrigger value="market">Market</TabsTrigger>
              <TabsTrigger value="resume">Resume</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Career Progress */}
                <Card className="lg:col-span-2 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">Career Progress</h3>
                    <Button variant="outline" size="sm">
                      <BarChart3 className="h-4 w-4 mr-2" />
                      View Details
                    </Button>
                  </div>

                  <div className="space-y-6">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Overall Progress</span>
                        <span className="text-sm text-gray-600">{overallSkillLevel}%</span>
                      </div>
                      <Progress value={overallSkillLevel} className="h-2" />
                    </div>

                    <Separator />

                    <div>
                      <h4 className="font-medium mb-3">Top Skills</h4>
                      <div className="space-y-3">
                        {careerData.skills
                          .sort((a, b) => b.level - a.level)
                          .slice(0, 4)
                          .map(skill => (
                            <div key={skill.name} className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <Badge className={getSkillCategoryColor(skill.category)}>
                                  {skill.category}
                                </Badge>
                                <span className="font-medium">{skill.name}</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <div className="w-20 h-2 bg-gray-200 rounded-full">
                                  <div 
                                    className="h-full bg-blue-500 rounded-full"
                                    style={{ width: `${skill.level}%` }}
                                  />
                                </div>
                                <span className="text-sm text-gray-600 w-8">
                                  {skill.level}%
                                </span>
                              </div>
                            </div>
                          ))}
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h4 className="font-medium mb-3">Recent Achievements</h4>
                      <div className="space-y-2">
                        {careerData.achievements.slice(0, 3).map(achievement => (
                          <div key={achievement.id} className="flex items-center space-x-3 p-2 bg-gray-50 rounded-lg">
                            <Award className="h-5 w-5 text-yellow-500" />
                            <div className="flex-1">
                              <p className="font-medium text-sm">{achievement.title}</p>
                              <p className="text-xs text-gray-600">{achievement.issuer} • {achievement.date}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Goals & Recommendations */}
                <div className="space-y-6">
                  {/* Active Goals */}
                  <Card className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold">Active Goals</h3>
                      <Button variant="ghost" size="sm">
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>

                    <div className="space-y-4">
                      {careerData.goals
                        .filter(goal => goal.status === 'in_progress')
                        .slice(0, 3)
                        .map(goal => (
                          <div key={goal.id} className="space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium">{goal.title}</span>
                              <span className="text-xs text-gray-600">
                                {goal.progress}%
                              </span>
                            </div>
                            <Progress value={goal.progress} className="h-1.5" />
                            <p className="text-xs text-gray-600">{goal.description}</p>
                          </div>
                        ))}
                    </div>
                  </Card>

                  {/* Recommendations */}
                  <Card className="p-6">
                    <h3 className="text-lg font-semibold mb-4">Recommendations</h3>
                    <div className="space-y-3">
                      {careerData.recommendations.slice(0, 3).map(rec => (
                        <div key={rec.id} className="p-3 border border-gray-200 rounded-lg">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-1">
                                <Badge variant={rec.priority === 'high' ? 'destructive' : rec.priority === 'medium' ? 'default' : 'secondary'} className="text-xs">
                                  {rec.priority}
                                </Badge>
                                <Badge variant="outline" className="text-xs">
                                  {rec.type}
                                </Badge>
                              </div>
                              <h4 className="font-medium text-sm">{rec.title}</h4>
                              <p className="text-xs text-gray-600 mt-1">{rec.description}</p>
                            </div>
                            <Button variant="ghost" size="sm" className="ml-2">
                              <ExternalLink className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>

                  {/* Profile Links */}
                  <Card className="p-6">
                    <h3 className="text-lg font-semibold mb-4">Professional Profiles</h3>
                    <div className="space-y-2">
                      <Button variant="outline" className="w-full justify-start" size="sm">
                        <Linkedin className="h-4 w-4 mr-2 text-blue-600" />
                        Connect LinkedIn Profile
                      </Button>
                      <Button variant="outline" className="w-full justify-start" size="sm">
                        <Github className="h-4 w-4 mr-2 text-gray-900" />
                        Connect GitHub Profile
                      </Button>
                      <Button variant="outline" className="w-full justify-start" size="sm">
                        <Globe className="h-4 w-4 mr-2 text-green-600" />
                        Add Portfolio Website
                      </Button>
                    </div>
                  </Card>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="pathways">
              <CareerPathways />
            </TabsContent>

            <TabsContent value="skills">
              <SkillsMatrix skills={careerData.skills} skillsByCategory={skillsByCategory} />
            </TabsContent>

            <TabsContent value="goals">
              <GoalTracker goals={careerData.goals} />
            </TabsContent>

            <TabsContent value="market">
              <MarketInsights />
            </TabsContent>

            <TabsContent value="resume">
              <ResumeBuilder />
            </TabsContent>
          </Tabs>
        </motion.div>
      </div>
    </ProtectedRoute>
  );
};

export default CareerPage;