'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '../../../store/slices/authSlice';
import ProfileActions from '../../../components/profile/ProfileActions';
import { Card } from '../../../components/ui/Card';
import ProtectedRoute from '../../../components/auth/ProtectedRoute';

const ProfileActionsPage = () => {
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Account Actions</h1>
          <p className="text-gray-600">Manage your account settings and security options</p>
        </div>

        {/* Profile Actions Card */}
        <Card className="p-6">
          <ProfileActions user={user} />
        </Card>
      </div>
    </ProtectedRoute>
  );
};

export default ProfileActionsPage;