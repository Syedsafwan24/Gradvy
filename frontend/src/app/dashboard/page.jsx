'use client';

import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { LogOut, User, Settings, Bell } from 'lucide-react';
import { selectCurrentUser } from '../../store/slices/authSlice';
import { useLogoutMutation } from '../../store/api/authApi';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import ProtectedRoute from '../../components/auth/ProtectedRoute';
import toast from 'react-hot-toast';

const DashboardPage = () => {
  const user = useSelector(selectCurrentUser);
  const router = useRouter();
  const [logout, { isLoading: isLoggingOut }] = useLogoutMutation();

  const handleLogout = async () => {
    try {
      // Call logout mutation - it will handle both success and error cases
      await logout();
      toast.success('Logged out successfully');
      router.push('/');
    } catch (error) {
      // This should rarely happen now, but just in case
      console.error('Logout error:', error);
      toast.success('Logged out successfully'); // Still show success since local state is cleared
      router.push('/');
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-gray-600">Welcome back, {user?.first_name}!</p>
              </div>
              <div className="flex items-center space-x-4">
                <Button variant="outline" size="sm">
                  <Bell className="h-4 w-4 mr-2" />
                  Notifications
                </Button>
                <Button variant="outline" size="sm">
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={handleLogout}
                  disabled={isLoggingOut}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  {isLoggingOut ? 'Logging out...' : 'Logout'}
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* User Info Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Card className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="bg-blue-100 p-3 rounded-full">
                    <User className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Profile</h3>
                    <p className="text-gray-600">Manage your account</p>
                  </div>
                </div>
                <div className="mt-4 space-y-2">
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Name:</span> {user?.first_name} {user?.last_name}
                  </p>
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Email:</span> {user?.email}
                  </p>
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Member since:</span>{' '}
                    {user?.date_joined ? new Date(user.date_joined).toLocaleDateString() : 'N/A'}
                  </p>
                  {user?.mfa_enrolled && (
                    <p className="text-sm text-green-600 font-medium">
                      ✓ Two-Factor Authentication Enabled
                    </p>
                  )}
                </div>
              </Card>
            </motion.div>

            {/* Quick Actions Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  <Button variant="outline" className="w-full justify-start">
                    Start Learning
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    Browse Courses
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    View Progress
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    Join Community
                  </Button>
                </div>
              </Card>
            </motion.div>

            {/* Stats Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Stats</h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Courses Completed</span>
                    <span className="font-semibold">0</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Hours Learned</span>
                    <span className="font-semibold">0</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Certificates Earned</span>
                    <span className="font-semibold">0</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Current Streak</span>
                    <span className="font-semibold">0 days</span>
                  </div>
                </div>
              </Card>
            </motion.div>
          </div>

          {/* Recent Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-8"
          >
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
              <div className="text-center py-8">
                <p className="text-gray-500">No recent activity to show.</p>
                <p className="text-sm text-gray-400 mt-2">
                  Start learning to see your progress here!
                </p>
              </div>
            </Card>
          </motion.div>

          {/* Welcome Message */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="mt-8"
          >
            <Card className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50">
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  🎉 Welcome to Gradvy!
                </h3>
                <p className="text-gray-600 mb-4">
                  You've successfully logged into your account. This is just the beginning of your learning journey!
                </p>
                <div className="flex flex-wrap gap-2 justify-center">
                  <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                    ✓ Authentication System
                  </span>
                  <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                    ✓ Redux State Management
                  </span>
                  <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                    ✓ Protected Routes
                  </span>
                  <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">
                    ✓ Auto Token Refresh
                  </span>
                </div>
              </div>
            </Card>
          </motion.div>
        </main>
      </div>
    </ProtectedRoute>
  );
};

export default DashboardPage;
