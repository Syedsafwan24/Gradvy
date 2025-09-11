'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/slices/authSlice';
import ProfileInfo from '@/components/profile/ProfileInfo';
import { Card } from '@/components/ui/card';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

const ProfileInfoPage = () => {
  const user = useSelector(selectCurrentUser);

  if (!user) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="p-6">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Personal Information</h1>
          <p className="text-gray-600">Update your personal details and information</p>
        </div>

        {/* Profile Information Card */}
        <Card className="p-6">
          <ProfileInfo user={user} />
        </Card>
      </div>
    </ProtectedRoute>
  );
};

export default ProfileInfoPage;