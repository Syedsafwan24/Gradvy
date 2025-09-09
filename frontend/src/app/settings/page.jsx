'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '../../store/slices/authSlice';
import GeneralSettings from '../../components/settings/GeneralSettings';
import { Card } from '../../components/ui/Card';
import ProtectedRoute from '../../components/auth/ProtectedRoute';

const SettingsPage = () => {
  const user = useSelector(selectCurrentUser);

  return (
    <ProtectedRoute requireAuth={true} redirectTo="/login">
      <div className="p-6">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">General Settings</h1>
          <p className="text-gray-600">Manage your basic account preferences and settings</p>
        </div>

        {/* General Settings Card */}
        <Card className="p-6">
          <GeneralSettings user={user} />
        </Card>
      </div>
    </ProtectedRoute>
  );
};

export default SettingsPage;