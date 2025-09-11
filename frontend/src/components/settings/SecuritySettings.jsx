'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { 
  Key, 
  Lock, 
  Eye, 
  EyeOff, 
  CheckCircle
} from 'lucide-react';
import { useChangePasswordMutation } from '@/store/api/authApi';
import { Button } from '../ui/Button';
import toast from 'react-hot-toast';

const passwordSchema = yup.object({
  old_password: yup.string().required('Current password is required'),
  new_password: yup
    .string()
    .min(8, 'Password must be at least 8 characters')
    .required('New password is required'),
  confirm_password: yup
    .string()
    .oneOf([yup.ref('new_password')], 'Passwords must match')
    .required('Please confirm your password'),
});

const SecuritySettings = ({ user }) => {
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [showPasswords, setShowPasswords] = useState({
    old: false,
    new: false,
    confirm: false
  });

  const [changePassword, { isLoading: isChangingPassword }] = useChangePasswordMutation();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm({
    resolver: yupResolver(passwordSchema),
    defaultValues: {
      old_password: '',
      new_password: '',
      confirm_password: '',
    }
  });

    const handlePasswordChange = async (data) => {
    try {
      await changePassword({
        current_password: data.old_password,
        new_password: data.new_password,
      }).unwrap();
      
      toast.success('Password changed successfully!');
      reset();
      setShowPasswordForm(false); // Hide form after successful change
    } catch (error) {
      console.error('Password change failed:', error);
      toast.error(error?.data?.message || 'Failed to change password. Please try again.');
    }
  };

  const togglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  return (
    <div className="space-y-8">
      {/* Section Header */}
      <div className="border-b pb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Password & Security</h2>
        <p className="text-gray-600">Manage your password and account security settings</p>
      </div>

      {/* Password Change */}
      <div className="border-b pb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <Key className="h-5 w-5 mr-2" />
              Change Password
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Update your password to keep your account secure
            </p>
          </div>
          <Button
            variant="outline"
            onClick={() => setShowPasswordForm(!showPasswordForm)}
          >
            {showPasswordForm ? 'Cancel' : 'Change Password'}
          </Button>
        </div>

        {showPasswordForm && (
          <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-6">
            <form onSubmit={handleSubmit(handlePasswordChange)} className="space-y-4 max-w-md">
          {/* Current Password */}
          <div>
            <label htmlFor="old_password" className="block text-sm font-medium text-gray-700 mb-1">
              Current Password
            </label>
            <div className="relative">
              <input
                {...register('old_password')}
                type={showPasswords.old ? 'text' : 'password'}
                id="old_password"
                className={`w-full px-3 py-2 pr-10 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.old_password ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={isChangingPassword}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => togglePasswordVisibility('old')}
              >
                {showPasswords.old ? (
                  <EyeOff className="h-4 w-4 text-gray-400" />
                ) : (
                  <Eye className="h-4 w-4 text-gray-400" />
                )}
              </button>
            </div>
            {errors.old_password && (
              <p className="mt-1 text-sm text-red-600">{errors.old_password.message}</p>
            )}
          </div>

          {/* New Password */}
          <div>
            <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 mb-1">
              New Password
            </label>
            <div className="relative">
              <input
                {...register('new_password')}
                type={showPasswords.new ? 'text' : 'password'}
                id="new_password"
                className={`w-full px-3 py-2 pr-10 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.new_password ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={isChangingPassword}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => togglePasswordVisibility('new')}
              >
                {showPasswords.new ? (
                  <EyeOff className="h-4 w-4 text-gray-400" />
                ) : (
                  <Eye className="h-4 w-4 text-gray-400" />
                )}
              </button>
            </div>
            {errors.new_password && (
              <p className="mt-1 text-sm text-red-600">{errors.new_password.message}</p>
            )}
          </div>

          {/* Confirm Password */}
          <div>
            <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-1">
              Confirm New Password
            </label>
            <div className="relative">
              <input
                {...register('confirm_password')}
                type={showPasswords.confirm ? 'text' : 'password'}
                id="confirm_password"
                className={`w-full px-3 py-2 pr-10 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.confirm_password ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={isChangingPassword}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => togglePasswordVisibility('confirm')}
              >
                {showPasswords.confirm ? (
                  <EyeOff className="h-4 w-4 text-gray-400" />
                ) : (
                  <Eye className="h-4 w-4 text-gray-400" />
                )}
              </button>
            </div>
            {errors.confirm_password && (
              <p className="mt-1 text-sm text-red-600">{errors.confirm_password.message}</p>
            )}
          </div>

          <Button
            type="submit"
            disabled={isChangingPassword}
          >
            <Lock className="h-4 w-4 mr-2" />
            {isChangingPassword ? 'Changing Password...' : 'Change Password'}
          </Button>
            </form>
          </div>
        )}
      </div>

      {/* Security Tips & Best Practices */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Security Best Practices</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Password Security */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-3">Password Security</h4>
            <ul className="space-y-2 text-sm text-blue-800">
              <li className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <span>Use a strong, unique password for your account</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <span>Change your password regularly</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <span>Never share your password with others</span>
              </li>
            </ul>
          </div>

          {/* Account Security */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-medium text-green-900 mb-3">Account Security</h4>
            <ul className="space-y-2 text-sm text-green-800">
              <li className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span>Enable two-factor authentication above</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span>Keep your backup codes safe and secure</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span>Log out from shared or public computers</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

    </div>
  );
};

export default SecuritySettings;