'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/slices/authSlice';
import AccountSettings from '@/components/settings/AccountSettings';
import { Card } from '@/components/ui/card';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

const AccountSettingsPage = () => {
  const user = useSelector(selectCurrentUser);

  return (
    <ProtectedRoute requireAuth={true} redirectTo="/login">
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