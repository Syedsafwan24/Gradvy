'use client';

import React, { useState } from 'react';
import { 
  Users, 
  MessageSquare, 
  Plus,
  TrendingUp,
  Award,
  HelpCircle,
  Lightbulb,
  Star,
  Eye,
  MessageCircle,
  ThumbsUp,
  Search,
  Flag
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import PageLayout from '@/components/layouts/PageLayout';

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
    return (
      <Card className="p-4 border border-gray-200 hover:shadow-md transition-shadow cursor-pointer">
        <div className="flex gap-3">
          <Avatar className="w-10 h-10 shrink-0">
            <AvatarFallback className="text-sm">
              {discussion.author.name.charAt(0)}
            </AvatarFallback>
          </Avatar>
          
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              {discussion.isAnswered && (
                <Badge variant="success" className="text-xs">
                  Answered
                </Badge>
              )}
              <Badge 
                variant={discussion.category === 'help' ? 'default' : 
                        discussion.category === 'showcase' ? 'purple' : 
                        discussion.category === 'resources' ? 'success' : 'secondary'}
                className="text-xs"
              >
                {categories.find(c => c.id === discussion.category)?.name}
              </Badge>
            </div>
            
            <h3 className="text-base sm:text-lg font-semibold mb-2 line-clamp-2 hover:text-primary">
              {discussion.title}
            </h3>
            
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {discussion.content}
            </p>
            
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <span className="font-medium truncate">{discussion.author.name}</span>
                <span>•</span>
                <span>{discussion.createdAt}</span>
              </div>
              
              <div className="flex items-center gap-3 sm:gap-4 text-xs text-gray-500">
                <span className="flex items-center gap-1">
                  <MessageCircle className="h-3 w-3" />
                  {discussion.replies}
                </span>
                <span className="flex items-center gap-1">
                  <ThumbsUp className="h-3 w-3" />
                  {discussion.likes}
                </span>
                <span className="flex items-center gap-1">
                  <Eye className="h-3 w-3" />
                  {discussion.views}
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
      <PageLayout
        title="Community"
        description={`${communityStats.totalMembers.toLocaleString()} members • ${communityStats.onlineMembers} online`}
        actions={
          <Button className="w-full sm:w-auto">
            <Plus className="h-4 w-4 mr-2" />
            New Discussion
          </Button>
        }
      >
        {/* Community Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 mb-6 sm:mb-8">
          <Card className="p-3 sm:p-4 text-center border border-gray-200 hover:shadow-md transition-shadow">
            <Users className="h-6 w-6 sm:h-8 sm:w-8 text-primary mx-auto mb-2" />
            <div className="text-lg sm:text-2xl font-bold text-gray-900">{communityStats.totalMembers.toLocaleString()}</div>
            <div className="text-xs text-gray-600">Members</div>
          </Card>
          
          <Card className="p-3 sm:p-4 text-center border border-gray-200 hover:shadow-md transition-shadow">
            <div className="relative inline-block">
              <Users className="h-6 w-6 sm:h-8 sm:w-8 text-success mx-auto mb-2" />
              <div className="absolute -top-1 -right-1 w-2 h-2 sm:w-3 sm:h-3 bg-success rounded-full"></div>
            </div>
            <div className="text-lg sm:text-2xl font-bold text-gray-900">{communityStats.onlineMembers}</div>
            <div className="text-xs text-gray-600">Online</div>
          </Card>
          
          <Card className="p-3 sm:p-4 text-center border border-gray-200 hover:shadow-md transition-shadow">
            <MessageSquare className="h-6 w-6 sm:h-8 sm:w-8 text-purple-500 mx-auto mb-2" />
            <div className="text-lg sm:text-2xl font-bold text-gray-900">{communityStats.totalPosts.toLocaleString()}</div>
            <div className="text-xs text-gray-600">Posts</div>
          </Card>
          
          <Card className="p-3 sm:p-4 text-center border border-gray-200 hover:shadow-md transition-shadow">
            <ThumbsUp className="h-6 w-6 sm:h-8 sm:w-8 text-warning mx-auto mb-2" />
            <div className="text-lg sm:text-2xl font-bold text-gray-900">{communityStats.totalAnswered.toLocaleString()}</div>
            <div className="text-xs text-gray-600">Answered</div>
          </Card>
          
          <Card className="p-3 sm:p-4 text-center border border-gray-200 hover:shadow-md transition-shadow">
            <Star className="h-6 w-6 sm:h-8 sm:w-8 text-yellow-500 mx-auto mb-2" />
            <div className="text-lg sm:text-2xl font-bold text-gray-900">{communityStats.helpfulAnswers.toLocaleString()}</div>
            <div className="text-xs text-gray-600">Helpful</div>
          </Card>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6 sm:mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search discussions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 h-11"
            />
          </div>
          
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-full sm:w-[180px] h-11">
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
            <SelectTrigger className="w-full sm:w-[180px] h-11">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="recent">Most Recent</SelectItem>
              <SelectItem value="popular">Most Popular</SelectItem>
              <SelectItem value="unanswered">Unanswered</SelectItem>
              <SelectItem value="trending">Trending</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Discussions */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base sm:text-lg font-semibold">
                {selectedCategory === 'all' ? 'All Discussions' : 
                 categories.find(c => c.id === selectedCategory)?.name}
              </h2>
              <span className="text-xs sm:text-sm text-gray-600">
                {filteredDiscussions.length} discussions
              </span>
            </div>

            {filteredDiscussions.length === 0 ? (
              <Card className="p-8 sm:p-12 text-center">
                <MessageSquare className="h-12 w-12 sm:h-16 sm:w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-2">No discussions found</h3>
                <p className="text-sm text-gray-600 mb-6">
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
          </div>

          {/* Sidebar */}
          <div className="space-y-4 sm:space-y-6">
            {/* Active Members */}
            <Card className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm sm:text-base font-semibold">Active Members</h3>
                <Badge variant="success" className="text-xs">{activeMembers.length} online</Badge>
              </div>
              <div className="space-y-3">
                {activeMembers.slice(0, 5).map(member => (
                  <div key={member.id} className="flex items-center gap-3">
                    <Avatar className="w-8 h-8">
                      <AvatarFallback className="text-xs">{member.name.charAt(0)}</AvatarFallback>
                    </Avatar>
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
              <Button variant="outline" className="w-full mt-4 h-9 text-sm">
                View All
              </Button>
            </Card>

            {/* Trending Tags */}
            <Card className="p-4 sm:p-6 hidden sm:block">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm sm:text-base font-semibold">Trending Tags</h3>
                <TrendingUp className="h-4 w-4 text-success" />
              </div>
              <div className="space-y-2">
                {trendingTags.map(tag => (
                  <div key={tag.name} className="flex items-center justify-between">
                    <span className="text-sm font-medium">#{tag.name}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500">{tag.count}</span>
                      <span className="text-xs text-success font-medium">{tag.trend}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Community Guidelines */}
            <Card className="p-4 sm:p-6 bg-primary/5 border-primary/20 hidden lg:block">
              <h3 className="text-sm font-semibold mb-3 text-primary">Community Guidelines</h3>
              <ul className="text-xs sm:text-sm text-gray-700 space-y-1">
                <li>• Be respectful and professional</li>
                <li>• Search before posting duplicates</li>
                <li>• Use clear, descriptive titles</li>
                <li>• Share code snippets when helpful</li>
                <li>• Give credit where due</li>
              </ul>
              <Button variant="outline" className="w-full mt-4 h-9 text-sm">
                Read Guidelines
              </Button>
            </Card>
          </div>
        </div>
      </PageLayout>
    </ProtectedRoute>
  );
};

export default CommunityPage;