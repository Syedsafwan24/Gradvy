'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  MessageSquare, 
  Heart,
  Share2,
  Search,
  Filter,
  Plus,
  TrendingUp,
  Calendar,
  Award,
  BookOpen,
  Code,
  HelpCircle,
  Lightbulb,
  Star,
  Eye,
  MessageCircle,
  ChevronRight,
  User,
  Clock,
  Pin,
  Flag,
  ThumbsUp,
  Hash,
  Bell
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Textarea } from '@/components/ui/textarea';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

const CommunityPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('recent');

  const communityStats = {
    totalMembers: 12500,
    onlineMembers: 450,
    totalPosts: 3280,
    totalAnswered: 2890,
    helpfulAnswers: 2150
  };

  const categories = [
    { id: 'all', name: 'All Discussions', count: 156, icon: MessageSquare },
    { id: 'help', name: 'Help & Questions', count: 45, icon: HelpCircle },
    { id: 'showcase', name: 'Project Showcase', count: 38, icon: Star },
    { id: 'resources', name: 'Resources & Tips', count: 28, icon: Lightbulb },
    { id: 'jobs', name: 'Career & Jobs', count: 22, icon: Award },
    { id: 'general', name: 'General Chat', count: 15, icon: MessageCircle },
    { id: 'feedback', name: 'Feedback', count: 8, icon: Flag }
  ];

  const discussions = [
    {
      id: 1,
      title: 'How to optimize React performance for large applications?',
      author: {
        name: 'Sarah Chen',
        avatar: '/api/placeholder/40/40',
        reputation: 2850,
        badge: 'React Expert'
      },
      category: 'help',
      content: 'I\'m working on a large React application with thousands of components and I\'m running into performance issues. What are the best practices for optimization?',
      tags: ['React', 'Performance', 'Optimization'],
      createdAt: '2 hours ago',
      replies: 12,
      likes: 24,
      views: 156,
      isAnswered: true,
      isPinned: false,
      lastActivity: '30 minutes ago'
    },
    {
      id: 2,
      title: 'My first full-stack project: E-commerce platform built with MERN',
      author: {
        name: 'Alex Rodriguez',
        avatar: '/api/placeholder/40/40',
        reputation: 1240,
        badge: 'Rising Star'
      },
      category: 'showcase',
      content: 'Just finished my first major project! It\'s an e-commerce platform with user authentication, payment processing, and admin dashboard. Would love to get some feedback!',
      tags: ['MERN', 'Full-Stack', 'E-commerce', 'Project'],
      createdAt: '4 hours ago',
      replies: 8,
      likes: 42,
      views: 89,
      isAnswered: false,
      isPinned: false,
      lastActivity: '1 hour ago'
    },
    {
      id: 3,
      title: '[PINNED] Welcome to the Gradvy Community! 🎉',
      author: {
        name: 'Gradvy Team',
        avatar: '/api/placeholder/40/40',
        reputation: 5000,
        badge: 'Moderator'
      },
      category: 'general',
      content: 'Welcome to our learning community! Here you can ask questions, share your projects, help others, and connect with fellow learners from around the world.',
      tags: ['Welcome', 'Community', 'Guidelines'],
      createdAt: '1 week ago',
      replies: 45,
      likes: 128,
      views: 1250,
      isAnswered: false,
      isPinned: true,
      lastActivity: '3 hours ago'
    },
    {
      id: 4,
      title: 'Best resources for learning system design?',
      author: {
        name: 'Emma Wilson',
        avatar: '/api/placeholder/40/40',
        reputation: 890,
        badge: 'Learner'
      },
      category: 'resources',
      content: 'I\'m preparing for senior developer interviews and need good resources for system design. Any recommendations for books, courses, or practice platforms?',
      tags: ['System Design', 'Interview Prep', 'Resources'],
      createdAt: '6 hours ago',
      replies: 15,
      likes: 18,
      views: 203,
      isAnswered: true,
      isPinned: false,
      lastActivity: '2 hours ago'
    },
    {
      id: 5,
      title: 'Remote developer job opportunities - Share your experience',
      author: {
        name: 'David Kim',
        avatar: '/api/placeholder/40/40',
        reputation: 1560,
        badge: 'Career Guru'
      },
      category: 'jobs',
      content: 'Looking to transition to remote work. What platforms do you recommend for finding quality remote developer positions? Any tips for remote interviews?',
      tags: ['Remote Work', 'Job Search', 'Career'],
      createdAt: '8 hours ago',
      replies: 22,
      likes: 35,
      views: 187,
      isAnswered: false,
      isPinned: false,
      lastActivity: '1 hour ago'
    }
  ];

  const activeMembers = [
    {
      id: 1,
      name: 'Sarah Chen',
      avatar: '/api/placeholder/40/40',
      status: 'online',
      reputation: 2850,
      badge: 'React Expert',
      contributions: 145
    },
    {
      id: 2,
      name: 'Mike Johnson',
      avatar: '/api/placeholder/40/40',
      status: 'online',
      reputation: 1920,
      badge: 'Full Stack Dev',
      contributions: 89
    },
    {
      id: 3,
      name: 'Lisa Garcia',
      avatar: '/api/placeholder/40/40',
      status: 'away',
      reputation: 1440,
      badge: 'UI/UX Designer',
      contributions: 67
    },
    {
      id: 4,
      name: 'Alex Thompson',
      avatar: '/api/placeholder/40/40',
      status: 'online',
      reputation: 2100,
      badge: 'Backend Specialist',
      contributions: 102
    }
  ];

  const trendingTags = [
    { name: 'React', count: 45, trend: '+12%' },
    { name: 'JavaScript', count: 38, trend: '+8%' },
    { name: 'Python', count: 32, trend: '+15%' },
    { name: 'Career', count: 28, trend: '+22%' },
    { name: 'Full-Stack', count: 25, trend: '+5%' },
    { name: 'Interview', count: 20, trend: '+18%' }
  ];

  const getCategoryIcon = (categoryId) => {
    const category = categories.find(c => c.id === categoryId);
    return category ? category.icon : MessageSquare;
  };

  const getCategoryColor = (categoryId) => {
    const colors = {
      'help': 'bg-blue-100 text-blue-700',
      'showcase': 'bg-purple-100 text-purple-700',
      'resources': 'bg-green-100 text-green-700',
      'jobs': 'bg-orange-100 text-orange-700',
      'general': 'bg-gray-100 text-gray-700',
      'feedback': 'bg-red-100 text-red-700'
    };
    return colors[categoryId] || 'bg-gray-100 text-gray-700';
  };

  const DiscussionCard = ({ discussion }) => {
    const CategoryIcon = getCategoryIcon(discussion.category);
    
    return (
      <Card className="p-6 hover:shadow-md transition-all duration-200">
        <div className="flex items-start space-x-4">
          <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-sm font-medium">{discussion.author.name.charAt(0)}</span>
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-2">
                {discussion.isPinned && (
                  <Pin className="h-4 w-4 text-green-600" />
                )}
                <Badge className={getCategoryColor(discussion.category)}>
                  <CategoryIcon className="h-3 w-3 mr-1" />
                  {categories.find(c => c.id === discussion.category)?.name}
                </Badge>
                {discussion.isAnswered && (
                  <Badge className="bg-green-100 text-green-700">
                    <ThumbsUp className="h-3 w-3 mr-1" />
                    Answered
                  </Badge>
                )}
              </div>
            </div>
            
            <h3 className="font-semibold text-lg mb-2 hover:text-blue-600 cursor-pointer">
              {discussion.title}
            </h3>
            
            <p className="text-gray-600 text-sm mb-3 line-clamp-2">
              {discussion.content}
            </p>
            
            <div className="flex flex-wrap gap-1 mb-3">
              {discussion.tags.map(tag => (
                <Badge key={tag} variant="outline" className="text-xs">
                  <Hash className="h-2 w-2 mr-1" />
                  {tag}
                </Badge>
              ))}
            </div>
            
            <div className="flex items-center justify-between text-sm text-gray-500">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-1">
                  <span className="font-medium">{discussion.author.name}</span>
                  <Badge variant="secondary" className="text-xs">
                    {discussion.author.badge}
                  </Badge>
                </div>
                <span className="flex items-center space-x-1">
                  <Clock className="h-3 w-3" />
                  <span>{discussion.createdAt}</span>
                </span>
              </div>
              
              <div className="flex items-center space-x-4">
                <span className="flex items-center space-x-1">
                  <MessageCircle className="h-3 w-3" />
                  <span>{discussion.replies}</span>
                </span>
                <span className="flex items-center space-x-1">
                  <Heart className="h-3 w-3" />
                  <span>{discussion.likes}</span>
                </span>
                <span className="flex items-center space-x-1">
                  <Eye className="h-3 w-3" />
                  <span>{discussion.views}</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </Card>
    );
  };

  const filteredDiscussions = discussions.filter(discussion => {
    const matchesSearch = discussion.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          discussion.content.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || discussion.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Community</h1>
            <p className="text-gray-600">
              Connect, learn, and grow together with fellow developers
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <Button variant="outline">
              <Bell className="h-4 w-4 mr-2" />
              Notifications
            </Button>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Discussion
            </Button>
          </div>
        </motion.div>

        {/* Community Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-5 gap-4"
        >
          <Card className="p-4 text-center">
            <Users className="h-8 w-8 text-blue-500 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{communityStats.totalMembers.toLocaleString()}</div>
            <div className="text-xs text-gray-600">Members</div>
          </Card>
          
          <Card className="p-4 text-center">
            <div className="relative">
              <Users className="h-8 w-8 text-green-500 mx-auto mb-2" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
            <div className="text-2xl font-bold text-gray-900">{communityStats.onlineMembers}</div>
            <div className="text-xs text-gray-600">Online Now</div>
          </Card>
          
          <Card className="p-4 text-center">
            <MessageSquare className="h-8 w-8 text-purple-500 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{communityStats.totalPosts.toLocaleString()}</div>
            <div className="text-xs text-gray-600">Discussions</div>
          </Card>
          
          <Card className="p-4 text-center">
            <ThumbsUp className="h-8 w-8 text-orange-500 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{communityStats.totalAnswered.toLocaleString()}</div>
            <div className="text-xs text-gray-600">Answered</div>
          </Card>
          
          <Card className="p-4 text-center">
            <Star className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">{communityStats.helpfulAnswers.toLocaleString()}</div>
            <div className="text-xs text-gray-600">Helpful</div>
          </Card>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex flex-col lg:flex-row gap-4"
        >
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search discussions, tags, or members..."
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

          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="lg:w-48">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="recent">Most Recent</SelectItem>
              <SelectItem value="popular">Most Popular</SelectItem>
              <SelectItem value="unanswered">Unanswered</SelectItem>
              <SelectItem value="trending">Trending</SelectItem>
            </SelectContent>
          </Select>
        </motion.div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Discussions */}
          <div className="lg:col-span-2 space-y-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">
                  {selectedCategory === 'all' ? 'All Discussions' : 
                   categories.find(c => c.id === selectedCategory)?.name}
                </h2>
                <span className="text-sm text-gray-600">
                  {filteredDiscussions.length} discussions
                </span>
              </div>

              {filteredDiscussions.length === 0 ? (
                <Card className="p-12 text-center">
                  <MessageSquare className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No discussions found</h3>
                  <p className="text-gray-600 mb-6">
                    {searchTerm ? "Try adjusting your search criteria." : "Be the first to start a discussion!"}
                  </p>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Start Discussion
                  </Button>
                </Card>
              ) : (
                <div className="space-y-4">
                  {filteredDiscussions.map(discussion => (
                    <DiscussionCard key={discussion.id} discussion={discussion} />
                  ))}
                </div>
              )}
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Post */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Card className="p-6">
                <h3 className="font-semibold mb-4">Quick Post</h3>
                <Textarea 
                  placeholder="What's on your mind? Ask a question or share something..."
                  className="mb-3"
                />
                <Button className="w-full">
                  <Plus className="h-4 w-4 mr-2" />
                  Post Discussion
                </Button>
              </Card>
            </motion.div>

            {/* Active Members */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
            >
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold">Active Members</h3>
                  <Badge variant="secondary">{activeMembers.length} online</Badge>
                </div>
                <div className="space-y-3">
                  {activeMembers.map(member => (
                    <div key={member.id} className="flex items-center space-x-3">
                      <div className="relative">
                        <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                          <span className="text-xs font-medium">{member.name.charAt(0)}</span>
                        </div>
                        <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white ${
                          member.status === 'online' ? 'bg-green-500' : 'bg-yellow-500'
                        }`}></div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{member.name}</p>
                        <p className="text-xs text-gray-500">{member.badge}</p>
                      </div>
                      <div className="text-xs text-gray-400">
                        {member.contributions}
                      </div>
                    </div>
                  ))}
                </div>
                <Button variant="outline" size="sm" className="w-full mt-4">
                  View All Members
                </Button>
              </Card>
            </motion.div>

            {/* Trending Tags */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 }}
            >
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold">Trending Tags</h3>
                  <TrendingUp className="h-4 w-4 text-green-500" />
                </div>
                <div className="space-y-2">
                  {trendingTags.map(tag => (
                    <div key={tag.name} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Hash className="h-3 w-3 text-gray-400" />
                        <span className="text-sm font-medium">{tag.name}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-gray-500">{tag.count}</span>
                        <span className="text-xs text-green-600">{tag.trend}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </motion.div>

            {/* Community Guidelines */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 }}
            >
              <Card className="p-6 bg-blue-50 border-blue-200">
                <h3 className="font-semibold mb-3 text-blue-900">Community Guidelines</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Be respectful and professional</li>
                  <li>• Search before posting duplicates</li>
                  <li>• Use clear, descriptive titles</li>
                  <li>• Share code snippets when helpful</li>
                  <li>• Give credit where due</li>
                </ul>
                <Button variant="outline" size="sm" className="w-full mt-4">
                  Read Full Guidelines
                </Button>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default CommunityPage;