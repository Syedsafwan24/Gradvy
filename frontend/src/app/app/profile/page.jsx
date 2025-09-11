'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/slices/authSlice';
import ProfileHeader from '@/components/profile/ProfileHeader';
import ProfileInfo from '@/components/profile/ProfileInfo';
import ProfileActions from '@/components/profile/ProfileActions';
import { Card } from '@/components/ui/card';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

const ProfilePage = () => {
  const user = useSelector(selectCurrentUser);

  return (
    <ProtectedRoute requireAuth={true} redirectTo="/login">
      <div className="p-6">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Profile Overview</h1>
          <p className="text-gray-600">Your account summary and key information</p>
        </div>

        {/* Profile Header Card - Overview Only */}
        <Card className="p-6">
          <ProfileHeader user={user} />
        </Card>
      </div>
    </ProtectedRoute>
  );
};

export default ProfilePage;