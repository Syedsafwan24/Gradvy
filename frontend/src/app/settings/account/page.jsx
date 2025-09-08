'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '../../../store/slices/authSlice';
import AccountSettings from '../../../components/settings/AccountSettings';
import { Card } from '../../../components/ui/Card';
import ProtectedRoute from '../../../components/auth/ProtectedRoute';

const AccountSettingsPage = () => {
  const user = useSelector(selectCurrentUser);

  if (!user) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-gray-600">Loading account settings...</p>
        </div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="p-6">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Account Settings</h1>
          <p className="text-gray-600">Manage your account and subscription settings</p>
        </div>

        {/* Account Settings Card */}
        <Card className="p-6">
          <AccountSettings user={user} />
        </Card>
      </div>
    </ProtectedRoute>
  );
};

export default AccountSettingsPage;