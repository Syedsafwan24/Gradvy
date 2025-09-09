'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { User, BookOpen, TrendingUp, Clock, Award } from 'lucide-react';
import { selectCurrentUser } from '../../store/slices/authSlice';
import { Card } from '../../components/ui/Card';
import ProtectedRoute from '../../components/auth/ProtectedRoute';
import ProfileCompletionCard from '../../components/dashboard/ProfileCompletionCard';
import { useProfileCompletionPrompts } from '../../hooks/useProfileCompletionPrompts';

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
      <div className="p-6">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Welcome back, {user?.first_name || 'User'}! Here's what's happening with your account.
          </p>
        </div>

        {/* User Profile Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <Card className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-xl font-semibold text-blue-700">
                    {user?.first_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                  </span>
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    {user?.first_name && user?.last_name 
                      ? `${user.first_name} ${user.last_name}`
                      : user?.email || 'User'}
                  </h2>
                  <p className="text-gray-600">{user?.email}</p>
                  <p className="text-sm text-gray-500">
                    Member since {formatJoinDate(user?.date_joined)}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                {user?.is_mfa_enabled && (
                  <div className="flex items-center space-x-2 bg-green-100 text-green-800 px-3 py-2 rounded-full text-sm font-medium">
                    <TrendingUp className="h-4 w-4" />
                    <span>2FA Protected</span>
                  </div>
                )}
                <div className="flex items-center space-x-2 bg-blue-100 text-blue-800 px-3 py-2 rounded-full text-sm font-medium">
                  <User className="h-4 w-4" />
                  <span>Active</span>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Profile Completion Card */}
        <ProfileCompletionCard user={user} />

        {/* Getting Started */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mb-8"
        >
          <Card className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200">
            <div className="flex items-start space-x-4">
              <div className="bg-blue-100 p-3 rounded-full">
                <BookOpen className="h-6 w-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Ready to start your learning journey?
                </h3>
                <p className="text-gray-700 mb-4">
                  Your account is set up and ready to go. Explore personalized learning paths, 
                  track your progress, and achieve your goals with AI-powered recommendations.
                </p>
                <div className="flex flex-wrap gap-3">
                  <div className="flex items-center space-x-2 bg-white bg-opacity-60 px-3 py-2 rounded-lg">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm font-medium">Account Active</span>
                  </div>
                  <div className="flex items-center space-x-2 bg-white bg-opacity-60 px-3 py-2 rounded-lg">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-sm font-medium">Profile Complete</span>
                  </div>
                  {user?.is_mfa_enabled && (
                    <div className="flex items-center space-x-2 bg-white bg-opacity-60 px-3 py-2 rounded-lg">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm font-medium">Security Enhanced</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Account Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Account Overview</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="bg-blue-100 p-4 rounded-full inline-flex items-center justify-center mb-3">
                  <User className="h-6 w-6 text-blue-600" />
                </div>
                <h4 className="font-medium text-gray-900">Profile</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Your account information and preferences are configured
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-green-100 p-4 rounded-full inline-flex items-center justify-center mb-3">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                </div>
                <h4 className="font-medium text-gray-900">Security</h4>
                <p className="text-sm text-gray-600 mt-1">
                  {user?.is_mfa_enabled 
                    ? 'Two-factor authentication is enabled'
                    : 'Consider enabling 2FA for better security'
                  }
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-purple-100 p-4 rounded-full inline-flex items-center justify-center mb-3">
                  <BookOpen className="h-6 w-6 text-purple-600" />
                </div>
                <h4 className="font-medium text-gray-900">Learning</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Ready to explore personalized learning paths
                </p>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
    </ProtectedRoute>
  );
};

export default DashboardPage;
