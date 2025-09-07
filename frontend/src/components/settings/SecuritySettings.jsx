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
import { useChangePasswordMutation } from '../../store/api/authApi';
import { Button } from '../ui/Button';
import toast from 'react-hot-toast';

const passwordSchema = yup.object({
  old_password: yup.string().required('Current password is required'),
  new_password: yup
    .string()
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Password must contain at least one lowercase letter, one uppercase letter, and one number'
    )
    .required('New password is required'),
  confirm_password: yup
    .string()
    .oneOf([yup.ref('new_password')], 'Passwords must match')
    .required('Please confirm your password'),
});

const SecuritySettings = ({ user }) => {
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
        old_password: data.old_password,
        new_password: data.new_password
      }).unwrap();
      reset();
      toast.success('Password changed successfully!');
    } catch (error) {
      console.error('Password change failed:', error);
      toast.error('Failed to change password. Please check your current password.');
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

      {/* Password Change */}
      <div className="border-b pb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          <Key className="h-5 w-5 inline mr-2" />
          Change Password
        </h3>
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

      {/* Security Tips */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Security Tips</h3>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <ul className="space-y-2 text-sm text-blue-800">
            <li className="flex items-start space-x-2">
              <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <span>Use a strong, unique password for your account</span>
            </li>
            <li className="flex items-start space-x-2">
              <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <span>Enable two-factor authentication for enhanced security</span>
            </li>
            <li className="flex items-start space-x-2">
              <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <span>Keep your backup codes in a safe, secure location</span>
            </li>
            <li className="flex items-start space-x-2">
              <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <span>Log out from shared or public computers</span>
            </li>
          </ul>
        </div>
      </div>

    </div>
  );
};

export default SecuritySettings;