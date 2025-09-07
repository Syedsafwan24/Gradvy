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
    <div className="min-h-screen bg-gray-50">
      {/* Full-width header */}
      <div className="w-full border-b bg-white shadow-sm">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16 3xl:px-24 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Settings</h1>
              <p className="text-gray-600">Manage your account preferences and security settings</p>
            </div>
            {/* Optional header actions */}
            <div className="hidden sm:flex items-center space-x-3">
              <span className="text-sm text-gray-500">Last updated: {new Date().toLocaleDateString()}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main content area with full-width responsive layout */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16 3xl:px-24 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Mobile-first navigation - full width on mobile, sidebar on desktop */}
          <aside className="lg:col-span-3 xl:col-span-2">
            <Card className="sticky top-6">
              <SettingsNav activeTab={activeTab} onTabChange={setActiveTab} />
            </Card>
          </aside>

          {/* Content area - full width on mobile, remaining space on desktop */}
          <main className="lg:col-span-9 xl:col-span-10">
            <div className="space-y-6">
              {/* Content card with responsive padding */}
              <Card className="overflow-hidden">
                <div className="p-4 sm:p-6 lg:p-8">
                  {renderActiveSection()}
                </div>
              </Card>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;