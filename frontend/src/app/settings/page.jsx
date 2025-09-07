'use client';

import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '../../store/slices/authSlice';
import SettingsNav from '../../components/settings/SettingsNav';
import GeneralSettings from '../../components/settings/GeneralSettings';
import SecuritySettings from '../../components/settings/SecuritySettings';
import PrivacySettings from '../../components/settings/PrivacySettings';
import AccountSettings from '../../components/settings/AccountSettings';
import { Card } from '../../components/ui/Card';

const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState('general');
  const user = useSelector(selectCurrentUser);

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  const renderActiveSection = () => {
    switch (activeTab) {
      case 'general':
        return <GeneralSettings user={user} />;
      case 'security':
        return <SecuritySettings user={user} />;
      case 'privacy':
        return <PrivacySettings user={user} />;
      case 'account':
        return <AccountSettings user={user} />;
      default:
        return <GeneralSettings user={user} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* Page Header */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Settings</h1>
            <p className="text-gray-600">Manage your account preferences and security settings</p>
          </div>

          <div className="lg:flex lg:space-x-6 space-y-6 lg:space-y-0">
            {/* Settings Navigation */}
            <div className="lg:w-1/4">
              <Card className="p-6">
                <SettingsNav activeTab={activeTab} onTabChange={setActiveTab} />
              </Card>
            </div>

            {/* Settings Content */}
            <div className="lg:w-3/4">
              <Card className="p-6">
                {renderActiveSection()}
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;