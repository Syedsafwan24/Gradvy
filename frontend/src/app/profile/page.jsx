'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '../../store/slices/authSlice';
import ProfileHeader from '../../components/profile/ProfileHeader';
import ProfileInfo from '../../components/profile/ProfileInfo';
import ProfileActions from '../../components/profile/ProfileActions';
import { Card } from '../../components/ui/Card';

const ProfilePage = () => {
  const user = useSelector(selectCurrentUser);

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* Page Header */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Profile</h1>
            <p className="text-gray-600">Manage your personal information and account settings</p>
          </div>

          {/* Profile Header Card */}
          <Card className="p-6">
            <ProfileHeader user={user} />
          </Card>

          {/* Profile Information */}
          <Card className="p-6">
            <ProfileInfo user={user} />
          </Card>

          {/* Quick Actions */}
          <Card className="p-6">
            <ProfileActions user={user} />
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;