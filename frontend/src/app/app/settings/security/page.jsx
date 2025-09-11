'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/slices/authSlice';
import MFAManager from '@/components/auth/MFA/MFAManager';
import SecuritySettings from '@/components/settings/SecuritySettings';
import { Card } from '@/components/ui/card';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

const SecurityPage = () => {
  const user = useSelector(selectCurrentUser);

  return (
    <ProtectedRoute requireAuth={true} redirectTo="/login">
      <div className="p-6">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Security Settings</h1>
          <p className="text-gray-600">Manage your account security and authentication methods</p>
        </div>

        <div className="space-y-8">
          {/* Two-Factor Authentication Section */}
          <Card className="p-6">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Two-Factor Authentication</h2>
              <p className="text-gray-600">Add an extra layer of security to your account with 2FA</p>
            </div>
            <MFAManager />
          </Card>

          {/* Password & Security Management */}
          <Card className="p-6">
            <SecuritySettings user={user} />
          </Card>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default SecurityPage;