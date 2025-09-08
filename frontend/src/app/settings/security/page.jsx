'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '../../../store/slices/authSlice';
import MFAManager from '../../../components/auth/MFA/MFAManager';
import SecuritySettings from '../../../components/settings/SecuritySettings';
import { Card } from '../../../components/ui/Card';
import ProtectedRoute from '../../../components/auth/ProtectedRoute';

const SecurityPage = () => {
  const user = useSelector(selectCurrentUser);

  if (!user) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-gray-600">Loading security settings...</p>
        </div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="p-6">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Security Settings</h1>
          <p className="text-gray-600">Manage your account security and authentication methods</p>
        </div>

        <div className="space-y-8">
          {/* MFA Management Section */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Two-Factor Authentication</h2>
            <MFAManager />
          </div>

          {/* Other Security Settings */}
          <Card className="p-6">
            <SecuritySettings user={user} />
          </Card>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default SecurityPage;