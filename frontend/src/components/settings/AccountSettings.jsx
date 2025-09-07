'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Trash2, AlertTriangle, LogOut, Download, RefreshCw, Clock, Mail } from 'lucide-react';
import { useLogoutMutation } from '../../store/api/authApi';
import { Button } from '../ui/Button';
import toast from 'react-hot-toast';

const AccountSettings = ({ user }) => {
  const router = useRouter();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  const [logout, { isLoading: isLoggingOut }] = useLogoutMutation();

  const handleLogoutAllDevices = async () => {
    if (window.confirm('Are you sure you want to log out from all devices? You will need to log in again.')) {
      try {
        await logout().unwrap();
        router.push('/login');
        toast.success('Logged out from all devices successfully');
      } catch (error) {
        console.error('Logout failed:', error);
        toast.error('Failed to log out from all devices. Please try again.');
      }
    }
  };

  const handleAccountDeactivation = () => {
    if (window.confirm('Are you sure you want to deactivate your account? You can reactivate it by logging in again.')) {
      toast.success('Account deactivation request submitted');
    }
  };

  const handleAccountDeletion = () => {
    if (deleteConfirmText !== 'DELETE MY ACCOUNT') {
      toast.error('Please type "DELETE MY ACCOUNT" exactly to confirm');
      return;
    }

    if (window.confirm('This action cannot be undone. Your account and all data will be permanently deleted.')) {
      toast.success('Account deletion request submitted. You will receive a confirmation email.');
      setShowDeleteConfirm(false);
      setDeleteConfirmText('');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not available';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Not available';
    }
  };

  return (
    <div className="space-y-8">
      {/* Section Header */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Account Settings</h2>
        <p className="text-gray-600">Manage your account status and advanced settings</p>
      </div>

      {/* Account Information */}
      <div className="border-b pb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Account Information</h3>
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <Mail className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Email Address</span>
              </div>
              <p className="text-gray-900">{user.email}</p>
            </div>
            
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <Clock className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Account Created</span>
              </div>
              <p className="text-gray-900">{formatDate(user.date_joined)}</p>
            </div>
            
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <RefreshCw className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Last Updated</span>
              </div>
              <p className="text-gray-900">{formatDate(user.updated_at)}</p>
            </div>
            
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <Clock className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Last Login</span>
              </div>
              <p className="text-gray-900">{formatDate(user.last_login)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Account Actions */}
      <div className="border-b pb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Account Actions</h3>
        <div className="space-y-4">
          {/* Export Account Data */}
          <div className="flex items-center justify-between py-3 px-4 border border-gray-200 rounded-lg">
            <div className="flex items-start space-x-3">
              <Download className="h-5 w-5 text-gray-500" />
              <div>
                <h4 className="text-sm font-medium text-gray-900">Export Account Data</h4>
                <p className="text-xs text-gray-600">Download all your account data in JSON format</p>
              </div>
            </div>
            <Button variant="outline" size="sm">
              Export Data
            </Button>
          </div>

          {/* Logout All Devices */}
          <div className="flex items-center justify-between py-3 px-4 border border-gray-200 rounded-lg">
            <div className="flex items-start space-x-3">
              <LogOut className="h-5 w-5 text-gray-500" />
              <div>
                <h4 className="text-sm font-medium text-gray-900">Logout All Devices</h4>
                <p className="text-xs text-gray-600">Sign out from all devices and browsers</p>
              </div>
            </div>
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleLogoutAllDevices}
              disabled={isLoggingOut}
            >
              {isLoggingOut ? 'Logging out...' : 'Logout All'}
            </Button>
          </div>

          {/* Account Deactivation */}
          <div className="flex items-center justify-between py-3 px-4 border border-yellow-200 bg-yellow-50 rounded-lg">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 text-yellow-600" />
              <div>
                <h4 className="text-sm font-medium text-yellow-900">Deactivate Account</h4>
                <p className="text-xs text-yellow-700">Temporarily disable your account (reversible)</p>
              </div>
            </div>
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleAccountDeactivation}
            >
              Deactivate
            </Button>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div>
        <h3 className="text-lg font-medium text-red-900 mb-4">
          <AlertTriangle className="h-5 w-5 inline mr-2" />
          Danger Zone
        </h3>
        
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6">
          <div className="space-y-4">
            <div>
              <h4 className="text-lg font-semibold text-red-900 mb-2">Delete Account</h4>
              <p className="text-sm text-red-700 mb-4">
                Once you delete your account, there is no going back. Please be certain. 
                This action will permanently delete your account and all associated data.
              </p>
            </div>

            {!showDeleteConfirm ? (
              <Button
                variant="destructive"
                onClick={() => setShowDeleteConfirm(true)}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete My Account
              </Button>
            ) : (
              <div className="space-y-4">
                <div className="bg-white border border-red-300 rounded-lg p-4">
                  <div className="space-y-3">
                    <div className="flex items-start space-x-3">
                      <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
                      <div>
                        <h5 className="font-semibold text-red-900">Are you absolutely sure?</h5>
                        <div className="text-sm text-red-700 mt-1 space-y-1">
                          <p>This action cannot be undone. This will permanently:</p>
                          <ul className="list-disc list-inside ml-4 space-y-1">
                            <li>Delete your account and profile</li>
                            <li>Remove all your data and activity</li>
                            <li>Cancel any active subscriptions</li>
                            <li>Revoke access to all connected applications</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <label htmlFor="delete-confirm" className="block text-sm font-medium text-red-900 mb-2">
                        Type "DELETE MY ACCOUNT" to confirm:
                      </label>
                      <input
                        id="delete-confirm"
                        type="text"
                        value={deleteConfirmText}
                        onChange={(e) => setDeleteConfirmText(e.target.value)}
                        className="w-full px-3 py-2 border border-red-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                        placeholder="DELETE MY ACCOUNT"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex space-x-3">
                  <Button
                    variant="destructive"
                    onClick={handleAccountDeletion}
                    disabled={deleteConfirmText !== 'DELETE MY ACCOUNT'}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Yes, Delete My Account
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowDeleteConfirm(false);
                      setDeleteConfirmText('');
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccountSettings;