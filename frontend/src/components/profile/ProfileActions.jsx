'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Settings, Shield, Key, LogOut } from 'lucide-react';
import { Button } from '../ui/Button';
import { useLogoutMutation } from '@/store/api/authApi';
import toast from 'react-hot-toast';

const ProfileActions = ({ user }) => {
  const router = useRouter();
  const [logout, { isLoading: isLoggingOut }] = useLogoutMutation();

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to log out?')) {
      try {
        await logout().unwrap();
        router.push('/login');
        toast.success('Logged out successfully');
      } catch (error) {
        console.error('Logout failed:', error);
        toast.error('Logout failed. Please try again.');
      }
    }
  };

  const actions = [
    {
      icon: Settings,
      title: 'Account Settings',
      description: 'Manage your account preferences and privacy settings',
      action: () => router.push('/app/settings'),
      variant: 'default'
    },
    {
      icon: Shield,
      title: user?.is_mfa_enabled ? 'Manage 2FA' : 'Enable 2FA',
      description: user?.is_mfa_enabled 
        ? 'View backup codes or disable two-factor authentication'
        : 'Secure your account with two-factor authentication',
      action: () => router.push('/app/settings/security'),
      variant: user?.is_mfa_enabled ? 'outline' : 'default'
    },
    {
      icon: Key,
      title: 'Change Password',
      description: 'Update your account password for better security',
      action: () => router.push('/app/settings/security'),
      variant: 'outline'
    }
  ];

  const dangerActions = [
    {
      icon: LogOut,
      title: 'Sign Out',
      description: 'Sign out of your account on this device',
      action: handleLogout,
      variant: 'outline',
      loading: isLoggingOut,
      disabled: isLoggingOut
    }
  ];

  return (
    <div className="space-y-6">
      {/* Quick Actions */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {actions.map((action, index) => {
            const Icon = action.icon;
            return (
              <div
                key={index}
                className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors cursor-pointer"
                onClick={action.action}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                      <Icon className="h-5 w-5 text-gray-600" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-gray-900 mb-1">
                      {action.title}
                    </h4>
                    <p className="text-xs text-gray-600">
                      {action.description}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Account Management */}
      <div className="border-t pt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Management</h3>
        <div className="space-y-3">
          {dangerActions.map((action, index) => {
            const Icon = action.icon;
            const isDestructive = action.variant === 'destructive';
            
            return (
              <div
                key={index}
                className="flex items-center justify-between py-3 px-4 border border-gray-200 rounded-lg"
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <Icon className={`h-5 w-5 ${isDestructive ? 'text-red-500' : 'text-gray-500'}`} />
                  </div>
                  <div>
                    <h4 className={`text-sm font-medium ${isDestructive ? 'text-red-900' : 'text-gray-900'} mb-1`}>
                      {action.title}
                    </h4>
                    <p className={`text-xs ${isDestructive ? 'text-red-600' : 'text-gray-600'}`}>
                      {action.description}
                    </p>
                  </div>
                </div>
                <Button
                  variant={action.variant}
                  size="sm"
                  onClick={action.action}
                  disabled={action.disabled}
                >
                  {action.loading ? 'Processing...' : action.title}
                </Button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Security Status */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Shield className={`h-5 w-5 mt-0.5 ${user?.is_mfa_enabled ? 'text-green-600' : 'text-yellow-600'}`} />
          <div>
            <h4 className="text-sm font-semibold text-blue-900 mb-1">
              Security Status: {user?.is_mfa_enabled ? 'Protected' : 'Basic'}
            </h4>
            <p className="text-xs text-blue-800">
              {user?.is_mfa_enabled 
                ? 'Your account is protected with two-factor authentication'
                : 'Consider enabling 2FA for enhanced security'
              }
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileActions;