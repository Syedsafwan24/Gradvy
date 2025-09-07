'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { selectCurrentUser } from '../../../store/slices/authSlice';
import MFAManager from '../../../components/auth/MFA/MFAManager';
import SecuritySettings from '../../../components/settings/SecuritySettings';
import { Button } from '../../../components/ui/Button';
import { Card } from '../../../components/ui/Card';

const SecurityPage = () => {
  const router = useRouter();
  const user = useSelector(selectCurrentUser);

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Loading security settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* Page Header with Back Button */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.back()}
                className="flex items-center"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">Security Settings</h1>
                <p className="text-gray-600">Manage your account security and authentication methods</p>
              </div>
            </div>
          </div>

          {/* MFA Management Section */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Two-Factor Authentication</h2>
            <MFAManager />
          </div>

          {/* Other Security Settings */}
          <Card className="p-6">
            <SecuritySettings user={user} />
          </Card>
        </div>
      </div>
    </div>
  );
};

export default SecurityPage;