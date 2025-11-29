'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { User, BookOpen, TrendingUp, Shield, Award, Target, Rocket } from 'lucide-react';
import { selectCurrentUser } from '@/store/slices/authSlice';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import ProfileCompletionCard from '@/components/dashboard/ProfileCompletionCard';
import { useProfileCompletionPrompts } from '@/hooks/useProfileCompletionPrompts';
import PageLayout from '@/components/layouts/PageLayout';
import SectionCard from '@/components/layouts/SectionCard';

const DashboardPage = () => {
  const user = useSelector(selectCurrentUser);
  const { showSuccessToast } = useProfileCompletionPrompts(user);

  const formatJoinDate = (dateString) => {
    if (!dateString) return 'Recently';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return 'Recently';
    }
  };

  return (
    <ProtectedRoute>
      <PageLayout
        title="Dashboard"
        description={`Welcome back, ${user?.first_name || 'User'}! Here's your learning overview.`}
      >
        {/* Quick Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6 sm:mb-8">
          <Card className="p-4 border border-gray-200 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs sm:text-sm text-gray-600">Active Courses</p>
                <p className="text-xl sm:text-2xl font-bold text-gray-900 mt-1">0</p>
              </div>
              <div className="p-2 bg-primary/10 rounded-lg">
                <BookOpen className="w-5 h-5 text-primary" />
              </div>
            </div>
          </Card>

          <Card className="p-4 border border-gray-200 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs sm:text-sm text-gray-600">Learning Paths</p>
                <p className="text-xl sm:text-2xl font-bold text-gray-900 mt-1">0</p>
              </div>
              <div className="p-2 bg-success/10 rounded-lg">
                <Target className="w-5 h-5 text-success" />
              </div>
            </div>
          </Card>

          <Card className="p-4 border border-gray-200 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs sm:text-sm text-gray-600">Achievements</p>
                <p className="text-xl sm:text-2xl font-bold text-gray-900 mt-1">0</p>
              </div>
              <div className="p-2 bg-warning/10 rounded-lg">
                <Award className="w-5 h-5 text-warning" />
              </div>
            </div>
          </Card>

          <Card className="p-4 border border-gray-200 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs sm:text-sm text-gray-600">Streak</p>
                <p className="text-xl sm:text-2xl font-bold text-gray-900 mt-1">0d</p>
              </div>
              <div className="p-2 bg-info/10 rounded-lg">
                <Rocket className="w-5 h-5 text-info" />
              </div>
            </div>
          </Card>
        </div>

        {/* User Profile Card */}
        <SectionCard className="mb-6 sm:mb-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            <Avatar className="w-16 h-16 sm:w-20 sm:h-20">
              <AvatarFallback className="text-lg sm:text-xl bg-primary/10 text-primary">
                {user?.first_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <h2 className="text-lg sm:text-xl font-semibold text-gray-900 truncate">
                {user?.first_name && user?.last_name 
                  ? `${user.first_name} ${user.last_name}`
                  : user?.email || 'User'}
              </h2>
              <p className="text-sm text-gray-600 truncate">{user?.email}</p>
              <p className="text-xs sm:text-sm text-gray-500 mt-1">
                Member since {formatJoinDate(user?.date_joined)}
              </p>
            </div>
            <div className="flex gap-2 w-full sm:w-auto">
              <Badge variant="success">Active</Badge>
              {user?.is_mfa_enabled && (
                <Badge variant="purple">
                  <Shield className="w-3 h-3 mr-1" />
                  2FA
                </Badge>
              )}
            </div>
          </div>
        </SectionCard>

        {/* Profile Completion Card */}
        <div className="mb-6 sm:mb-8">
          <ProfileCompletionCard user={user} />
        </div>

        {/* Getting Started */}
        <SectionCard 
          className="mb-6 sm:mb-8 bg-primary/5 border-primary/20"
        >
          <div className="flex flex-col sm:flex-row items-start gap-4">
            <div className="p-3 bg-primary/10 rounded-lg shrink-0">
              <Rocket className="w-6 h-6 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-2">
                Ready to start your learning journey?
              </h3>
              <p className="text-sm text-gray-700 mb-4">
                Your account is set up and ready to go. Explore personalized learning paths, 
                track your progress, and achieve your goals with AI-powered recommendations.
              </p>
              <div className="flex flex-wrap gap-2">
                <Badge variant="success" className="text-xs">
                  Account Active
                </Badge>
                <Badge variant="default" className="text-xs">
                  Profile Complete
                </Badge>
                {user?.is_mfa_enabled && (
                  <Badge variant="purple" className="text-xs">
                    Security Enhanced
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </SectionCard>

        {/* Account Overview */}
        <SectionCard title="Account Overview">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6">
            <div className="text-center p-4">
              <div className="inline-flex items-center justify-center w-12 h-12 sm:w-14 sm:h-14 bg-primary/10 rounded-lg mb-3">
                <User className="w-6 h-6 text-primary" />
              </div>
              <h4 className="text-sm sm:text-base font-semibold text-gray-900">Profile</h4>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Your account information and preferences are configured
              </p>
            </div>
            
            <div className="text-center p-4">
              <div className="inline-flex items-center justify-center w-12 h-12 sm:w-14 sm:h-14 bg-success/10 rounded-lg mb-3">
                <Shield className="w-6 h-6 text-success" />
              </div>
              <h4 className="text-sm sm:text-base font-semibold text-gray-900">Security</h4>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                {user?.is_mfa_enabled 
                  ? 'Two-factor authentication is enabled'
                  : 'Consider enabling 2FA for better security'
                }
              </p>
            </div>
            
            <div className="text-center p-4">
              <div className="inline-flex items-center justify-center w-12 h-12 sm:w-14 sm:h-14 bg-warning/10 rounded-lg mb-3">
                <BookOpen className="w-6 h-6 text-warning" />
              </div>
              <h4 className="text-sm sm:text-base font-semibold text-gray-900">Learning</h4>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Ready to explore personalized learning paths
              </p>
            </div>
          </div>
        </SectionCard>
      </PageLayout>
    </ProtectedRoute>
  );
};

export default DashboardPage;
