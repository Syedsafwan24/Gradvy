'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Award, 
  Trophy, 
  Star, 
  Medal,
  Target,
  Flame,
  Calendar,
  TrendingUp,
  Users,
  Code,
  BookOpen,
  Zap,
  Crown,
  Badge as BadgeIcon,
  Lock,
  CheckCircle,
  Share2,
  Download
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

const AchievementsPage = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');

  const userStats = {
    totalPoints: 2750,
    level: 12,
    levelProgress: 65,
    pointsToNextLevel: 450,
    streak: 15,
    totalBadges: 18,
    completedCourses: 7,
    projectsCompleted: 5,
    rank: 'Intermediate Developer',
    position: 42
  };

  const categories = [
    { id: 'all', name: 'All Achievements', count: 45 },
    { id: 'learning', name: 'Learning', count: 15 },
    { id: 'projects', name: 'Projects', count: 10 },
    { id: 'community', name: 'Community', count: 8 },
    { id: 'streaks', name: 'Streaks', count: 7 },
    { id: 'special', name: 'Special', count: 5 }
  ];

  const achievements = [
    {
      id: 1,
      title: 'First Steps',
      description: 'Complete your first course on Gradvy',
      category: 'learning',
      points: 50,
      icon: BookOpen,
      color: 'bg-green-500',
      rarity: 'common',
      earned: true,
      earnedAt: '2024-01-15',
      progress: 100,
      requirements: ['Complete 1 course']
    },
    {
      id: 2,
      title: 'Code Master',
      description: 'Complete 100 coding challenges',
      category: 'learning',
      points: 200,
      icon: Code,
      color: 'bg-blue-500',
      rarity: 'rare',
      earned: true,
      earnedAt: '2024-02-20',
      progress: 100,
      requirements: ['Complete 100 coding challenges']
    },
    {
      id: 3,
      title: 'Project Pioneer',
      description: 'Create and share your first project',
      category: 'projects',
      points: 100,
      icon: Target,
      color: 'bg-purple-500',
      rarity: 'uncommon',
      earned: true,
      earnedAt: '2024-01-28',
      progress: 100,
      requirements: ['Create 1 public project']
    },
    {
      id: 4,
      title: 'Streak Master',
      description: 'Maintain a 30-day learning streak',
      category: 'streaks',
      points: 300,
      icon: Flame,
      color: 'bg-orange-500',
      rarity: 'epic',
      earned: false,
      earnedAt: null,
      progress: 50,
      requirements: ['Learn for 30 consecutive days'],
      currentStreak: 15
    },
    {
      id: 5,
      title: 'Community Helper',
      description: 'Help 50 community members',
      category: 'community',
      points: 250,
      icon: Users,
      color: 'bg-pink-500',
      rarity: 'rare',
      earned: false,
      earnedAt: null,
      progress: 24,
      requirements: ['Help 50 community members'],
      currentProgress: 12
    },
    {
      id: 6,
      title: 'JavaScript Ninja',
      description: 'Master JavaScript fundamentals and advanced concepts',
      category: 'learning',
      points: 400,
      icon: Zap,
      color: 'bg-yellow-500',
      rarity: 'legendary',
      earned: true,
      earnedAt: '2024-02-10',
      progress: 100,
      requirements: [
        'Complete JavaScript basics course',
        'Complete advanced JavaScript course',
        'Build 3 JavaScript projects'
      ]
    },
    {
      id: 7,
      title: 'Full Stack Champion',
      description: 'Complete both frontend and backend learning paths',
      category: 'learning',
      points: 500,
      icon: Crown,
      color: 'bg-indigo-500',
      rarity: 'legendary',
      earned: false,
      earnedAt: null,
      progress: 75,
      requirements: [
        'Complete frontend learning path',
        'Complete backend learning path',
        'Build full-stack project'
      ]
    },
    {
      id: 8,
      title: 'Early Adopter',
      description: 'Joined Gradvy in the first month',
      category: 'special',
      points: 150,
      icon: BadgeIcon,
      color: 'bg-teal-500',
      rarity: 'special',
      earned: true,
      earnedAt: '2024-01-01',
      progress: 100,
      requirements: ['Join Gradvy before February 2024']
    },
    {
      id: 9,
      title: 'Knowledge Seeker',
      description: 'Complete 10 different courses',
      category: 'learning',
      points: 300,
      icon: BookOpen,
      color: 'bg-green-500',
      rarity: 'epic',
      earned: false,
      earnedAt: null,
      progress: 70,
      requirements: ['Complete 10 different courses'],
      currentProgress: 7
    },
    {
      id: 10,
      title: 'Portfolio Master',
      description: 'Create 10 portfolio projects',
      category: 'projects',
      points: 400,
      icon: Trophy,
      color: 'bg-gold-500',
      rarity: 'epic',
      earned: false,
      earnedAt: null,
      progress: 50,
      requirements: ['Create 10 portfolio projects'],
      currentProgress: 5
    }
  ];

  const getRarityColor = (rarity) => {
    switch (rarity) {
      case 'common': return 'bg-gray-100 text-gray-700 border-gray-300';
      case 'uncommon': return 'bg-green-100 text-green-700 border-green-300';
      case 'rare': return 'bg-blue-100 text-blue-700 border-blue-300';
      case 'epic': return 'bg-purple-100 text-purple-700 border-purple-300';
      case 'legendary': return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      case 'special': return 'bg-pink-100 text-pink-700 border-pink-300';
      default: return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const getRarityName = (rarity) => {
    return rarity.charAt(0).toUpperCase() + rarity.slice(1);
  };

  const AchievementCard = ({ achievement }) => {
    const Icon = achievement.icon;
    const isEarned = achievement.earned;

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ scale: 1.02 }}
        className={`group ${!isEarned ? 'opacity-75' : ''}`}
      >
        <Card className={`p-6 hover:shadow-lg transition-all duration-300 ${!isEarned ? 'bg-gray-50' : 'bg-white'}`}>
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className={`p-3 rounded-full ${isEarned ? achievement.color : 'bg-gray-300'} relative`}>
                <Icon className={`h-6 w-6 ${isEarned ? 'text-white' : 'text-gray-500'}`} />
                {!isEarned && (
                  <Lock className="absolute inset-0 h-6 w-6 text-gray-600 m-auto" />
                )}
              </div>
              <div>
                <h3 className={`font-semibold text-lg ${!isEarned ? 'text-gray-600' : 'text-gray-900'}`}>
                  {achievement.title}
                </h3>
                <Badge className={`${getRarityColor(achievement.rarity)} text-xs`}>
                  {getRarityName(achievement.rarity)}
                </Badge>
              </div>
            </div>
            
            {isEarned && (
              <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <Share2 className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>

          <p className={`text-sm mb-4 ${!isEarned ? 'text-gray-500' : 'text-gray-600'}`}>
            {achievement.description}
          </p>

          {/* Progress Bar */}
          {!isEarned && achievement.progress < 100 && (
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-gray-600">Progress</span>
                <span className="text-xs text-gray-600">{achievement.progress}%</span>
              </div>
              <Progress value={achievement.progress} className="h-2" />
              {achievement.currentProgress && (
                <p className="text-xs text-gray-500 mt-1">
                  Current: {achievement.currentProgress} / {achievement.requirements[0].match(/\d+/)?.[0] || 'Goal'}
                </p>
              )}
            </div>
          )}

          {/* Requirements */}
          <div className="mb-4">
            <span className="text-xs font-medium text-gray-700 mb-2 block">Requirements:</span>
            <ul className="text-xs text-gray-600 space-y-1">
              {achievement.requirements.map((req, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <CheckCircle className={`h-3 w-3 mt-0.5 ${isEarned ? 'text-green-500' : 'text-gray-400'}`} />
                  <span>{req}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-1">
                <Star className={`h-4 w-4 ${isEarned ? 'text-yellow-500' : 'text-gray-400'}`} />
                <span className={`text-sm font-medium ${!isEarned ? 'text-gray-500' : 'text-gray-900'}`}>
                  {achievement.points} pts
                </span>
              </div>
              {isEarned && achievement.earnedAt && (
                <span className="text-xs text-gray-500">
                  Earned {new Date(achievement.earnedAt).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
        </Card>
      </motion.div>
    );
  };

  const filteredAchievements = achievements.filter(achievement => {
    const matchesCategory = selectedCategory === 'all' || achievement.category === selectedCategory;
    const matchesStatus = selectedStatus === 'all' || 
                         (selectedStatus === 'earned' && achievement.earned) ||
                         (selectedStatus === 'unearned' && !achievement.earned);
    
    return matchesCategory && matchesStatus;
  });

  const earnedAchievements = achievements.filter(a => a.earned);
  const totalPoints = earnedAchievements.reduce((sum, a) => sum + a.points, 0);
  const completionRate = (earnedAchievements.length / achievements.length) * 100;

  return (
    <ProtectedRoute>
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-8 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg"
        >
          <Trophy className="h-16 w-16 text-yellow-600 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Achievements</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Track your progress and earn badges as you learn, build, and contribute to the community.
          </p>
        </motion.div>

        {/* User Stats Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          <Card className="p-6 bg-gradient-to-br from-blue-500 to-blue-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100">Total Points</p>
                <p className="text-3xl font-bold">{totalPoints.toLocaleString()}</p>
              </div>
              <Star className="h-12 w-12 text-blue-200" />
            </div>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-green-500 to-green-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100">Level</p>
                <p className="text-3xl font-bold">{userStats.level}</p>
                <div className="mt-2">
                  <Progress value={userStats.levelProgress} className="h-2 bg-green-400" />
                  <p className="text-xs text-green-100 mt-1">
                    {userStats.pointsToNextLevel} to next level
                  </p>
                </div>
              </div>
              <TrendingUp className="h-12 w-12 text-green-200" />
            </div>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-orange-500 to-orange-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100">Current Streak</p>
                <p className="text-3xl font-bold">{userStats.streak} days</p>
              </div>
              <Flame className="h-12 w-12 text-orange-200" />
            </div>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100">Badges Earned</p>
                <p className="text-3xl font-bold">{earnedAchievements.length}/{achievements.length}</p>
                <p className="text-xs text-purple-100 mt-1">
                  {Math.round(completionRate)}% complete
                </p>
              </div>
              <Award className="h-12 w-12 text-purple-200" />
            </div>
          </Card>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex flex-col sm:flex-row gap-4"
        >
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="sm:w-48">
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

          <Select value={selectedStatus} onValueChange={setSelectedStatus}>
            <SelectTrigger className="sm:w-48">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Achievements</SelectItem>
              <SelectItem value="earned">Earned</SelectItem>
              <SelectItem value="unearned">Not Earned</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="outline" className="ml-auto">
            <Download className="h-4 w-4 mr-2" />
            Export Badge Collection
          </Button>
        </motion.div>

        {/* Achievements Content */}
        <Tabs defaultValue="all-achievements">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="all-achievements">All</TabsTrigger>
            <TabsTrigger value="recent">Recent</TabsTrigger>
            <TabsTrigger value="in-progress">In Progress</TabsTrigger>
            <TabsTrigger value="leaderboard">Leaderboard</TabsTrigger>
            <TabsTrigger value="milestones">Milestones</TabsTrigger>
          </TabsList>

          <TabsContent value="all-achievements" className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {filteredAchievements.map(achievement => (
                <AchievementCard key={achievement.id} achievement={achievement} />
              ))}
            </motion.div>
          </TabsContent>

          <TabsContent value="recent" className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {earnedAchievements
                .sort((a, b) => new Date(b.earnedAt) - new Date(a.earnedAt))
                .slice(0, 6)
                .map(achievement => (
                  <AchievementCard key={achievement.id} achievement={achievement} />
                ))}
            </motion.div>
          </TabsContent>

          <TabsContent value="in-progress" className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {achievements
                .filter(a => !a.earned && a.progress > 0)
                .map(achievement => (
                  <AchievementCard key={achievement.id} achievement={achievement} />
                ))}
            </motion.div>
          </TabsContent>

          <TabsContent value="leaderboard" className="mt-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Global Leaderboard</h3>
              <div className="space-y-4">
                {[
                  { rank: 1, name: 'Alex Chen', points: 5420, badges: 28 },
                  { rank: 2, name: 'Sarah Wilson', points: 4890, badges: 26 },
                  { rank: 3, name: 'Mike Rodriguez', points: 4350, badges: 24 },
                  { rank: 42, name: 'You', points: totalPoints, badges: earnedAchievements.length, isUser: true }
                ].map((user) => (
                  <div
                    key={user.rank}
                    className={`flex items-center justify-between p-4 rounded-lg ${
                      user.isUser ? 'bg-blue-50 border-2 border-blue-200' : 'bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center space-x-4">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                        user.rank === 1 ? 'bg-yellow-500 text-white' :
                        user.rank === 2 ? 'bg-gray-400 text-white' :
                        user.rank === 3 ? 'bg-orange-500 text-white' :
                        'bg-gray-200 text-gray-700'
                      }`}>
                        {user.rank}
                      </div>
                      <div>
                        <p className={`font-medium ${user.isUser ? 'text-blue-900' : 'text-gray-900'}`}>
                          {user.name}
                        </p>
                        <p className="text-sm text-gray-600">
                          {user.badges} badges earned
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-bold ${user.isUser ? 'text-blue-900' : 'text-gray-900'}`}>
                        {user.points.toLocaleString()} pts
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="milestones" className="mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Upcoming Milestones</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Crown className="h-6 w-6 text-yellow-600" />
                      <div>
                        <p className="font-medium">Level 15</p>
                        <p className="text-sm text-gray-600">450 points to go</p>
                      </div>
                    </div>
                    <Progress value={65} className="w-24 h-2" />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Trophy className="h-6 w-6 text-blue-600" />
                      <div>
                        <p className="font-medium">100 Day Streak</p>
                        <p className="text-sm text-gray-600">85 days to go</p>
                      </div>
                    </div>
                    <Progress value={15} className="w-24 h-2" />
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Achievement Stats</h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span>Completion Rate</span>
                    <span className="font-medium">{Math.round(completionRate)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Rarest Badge</span>
                    <span className="font-medium">JavaScript Ninja</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Points This Month</span>
                    <span className="font-medium">450</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Global Rank</span>
                    <span className="font-medium">#42</span>
                  </div>
                </div>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </ProtectedRoute>
  );
};

export default AchievementsPage;