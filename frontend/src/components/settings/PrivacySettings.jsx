'use client';

import React, { useState } from 'react';
import { Eye, Download, Trash2, Shield, Globe, Lock } from 'lucide-react';
import { Button } from '../ui/Button';
import toast from 'react-hot-toast';

const PrivacySettings = ({ user }) => {
  const [privacySettings, setPrivacySettings] = useState({
    profileVisibility: 'public',
    searchable: true,
    activityTracking: true,
    dataCollection: false,
    emailSharing: false
  });

  const handlePrivacyChange = (setting, value) => {
    setPrivacySettings(prev => ({
      ...prev,
      [setting]: value
    }));
    toast.success('Privacy setting updated');
  };

  const handleDataExport = () => {
    toast.success('Data export request submitted. You will receive an email when ready.');
  };

  const handleDataDeletion = () => {
    if (window.confirm('Are you sure you want to request data deletion? This action cannot be undone.')) {
      toast.success('Data deletion request submitted.');
    }
  };

  return (
    <div className="space-y-8">
      {/* Section Header */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Privacy Settings</h2>
        <p className="text-gray-600">Control how your information is collected, used, and shared</p>
      </div>

      {/* Privacy Controls */}
      <div className="border-b pb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          <Eye className="h-5 w-5 inline mr-2" />
          Privacy Controls
        </h3>
        
        <div className="space-y-6">
          {/* Profile Visibility */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Profile Visibility</label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="profileVisibility"
                  value="public"
                  checked={privacySettings.profileVisibility === 'public'}
                  onChange={(e) => handlePrivacyChange('profileVisibility', e.target.value)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span className="ml-2 text-sm text-gray-900">Public - Anyone can view your profile</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="profileVisibility"
                  value="private"
                  checked={privacySettings.profileVisibility === 'private'}
                  onChange={(e) => handlePrivacyChange('profileVisibility', e.target.value)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span className="ml-2 text-sm text-gray-900">Private - Only you can view your profile</span>
              </label>
            </div>
          </div>

          {/* Other Privacy Settings */}
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3">
              <div>
                <label className="text-sm font-medium text-gray-900">Allow search engines to find your profile</label>
                <p className="text-xs text-gray-600">Make your profile discoverable via search engines</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={privacySettings.searchable}
                  onChange={(e) => handlePrivacyChange('searchable', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between py-3">
              <div>
                <label className="text-sm font-medium text-gray-900">Activity tracking</label>
                <p className="text-xs text-gray-600">Allow us to track your activity for better recommendations</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={privacySettings.activityTracking}
                  onChange={(e) => handlePrivacyChange('activityTracking', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between py-3">
              <div>
                <label className="text-sm font-medium text-gray-900">Data collection for analytics</label>
                <p className="text-xs text-gray-600">Help improve our service by sharing anonymous usage data</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={privacySettings.dataCollection}
                  onChange={(e) => handlePrivacyChange('dataCollection', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between py-3">
              <div>
                <label className="text-sm font-medium text-gray-900">Share email with partners</label>
                <p className="text-xs text-gray-600">Allow trusted partners to send you relevant offers</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={privacySettings.emailSharing}
                  onChange={(e) => handlePrivacyChange('emailSharing', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Data Rights */}
      <div className="border-b pb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          <Shield className="h-5 w-5 inline mr-2" />
          Your Data Rights
        </h3>
        
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <Download className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-medium text-blue-900">Export Your Data</h4>
                <p className="text-sm text-blue-700 mt-1">
                  Download a copy of all your data in a portable format
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-3"
                  onClick={handleDataExport}
                >
                  Request Data Export
                </Button>
              </div>
            </div>
          </div>

          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <Trash2 className="h-5 w-5 text-red-600 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-medium text-red-900">Delete Your Data</h4>
                <p className="text-sm text-red-700 mt-1">
                  Request permanent deletion of your account and all associated data
                </p>
                <Button
                  variant="destructive"
                  size="sm"
                  className="mt-3"
                  onClick={handleDataDeletion}
                >
                  Request Data Deletion
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Cookies & Tracking */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          <Globe className="h-5 w-5 inline mr-2" />
          Cookies & Tracking
        </h3>
        
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <p className="text-sm text-gray-700 mb-4">
            We use cookies and similar technologies to enhance your experience and provide personalized content.
          </p>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm font-medium text-gray-900">Essential cookies</span>
                <p className="text-xs text-gray-600">Required for the website to function properly</p>
              </div>
              <div className="text-sm text-gray-500">Always active</div>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm font-medium text-gray-900">Analytics cookies</span>
                <p className="text-xs text-gray-600">Help us understand how you use our website</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={privacySettings.dataCollection}
                  onChange={(e) => handlePrivacyChange('dataCollection', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
          
          <Button variant="outline" size="sm" className="mt-4">
            <Lock className="h-4 w-4 mr-2" />
            Cookie Preferences
          </Button>
        </div>
      </div>
    </div>
  );
};

export default PrivacySettings;