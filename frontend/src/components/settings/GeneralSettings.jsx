'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Save, User, Mail, Phone, Globe, Bell, Moon, Sun } from 'lucide-react';
import { useUpdateProfileMutation } from '@/store/api/authApi';
import { Button } from '../ui/Button';
import toast from 'react-hot-toast';

const generalSettingsSchema = yup.object({
  first_name: yup.string().required('First name is required'),
  last_name: yup.string().required('Last name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  phone: yup.string().nullable(),
  bio: yup.string().max(500, 'Bio must be less than 500 characters').nullable(),
});

const GeneralSettings = ({ user }) => {
  const [updateProfile, { isLoading }] = useUpdateProfileMutation();
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    sms: false
  });
  const [theme, setTheme] = useState('light');

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty }
  } = useForm({
    resolver: yupResolver(generalSettingsSchema),
    defaultValues: {
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      email: user.email || '',
      phone: user.profile?.phone_number || '',
      bio: user.profile?.bio || '',
    }
  });

  const onSubmit = async (data) => {
    try {
      // Transform data to match backend API expectations
      const profileData = {
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        phone: data.phone || '',
        bio: data.bio || '',
      };

      await updateProfile(profileData).unwrap();
      toast.success('Profile updated successfully!');
    } catch (error) {
      console.error('Profile update failed:', error);
      const errorMessage = error?.data?.message || 
                          error?.data?.email?.[0] || 
                          error?.data?.phone?.[0] || 
                          'Failed to update profile. Please try again.';
      toast.error(errorMessage);
    }
  };

  const handleNotificationChange = (type, value) => {
    setNotifications(prev => ({
      ...prev,
      [type]: value
    }));
    toast.success(`${type.charAt(0).toUpperCase() + type.slice(1)} notifications ${value ? 'enabled' : 'disabled'}`);
  };

  return (
    <div className="space-y-8">
      {/* Section Header */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">General Settings</h2>
        <p className="text-gray-600">Update your personal information and preferences</p>
      </div>

      {/* Profile Information */}
      <div className="border-b pb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Information</h3>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* First Name */}
            <div>
              <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-2">
                <User className="h-4 w-4 inline mr-2" />
                First Name
              </label>
              <input
                {...register('first_name')}
                type="text"
                id="first_name"
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.first_name ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={isLoading}
              />
              {errors.first_name && (
                <p className="mt-1 text-sm text-red-600">{errors.first_name.message}</p>
              )}
            </div>

            {/* Last Name */}
            <div>
              <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-2">
                <User className="h-4 w-4 inline mr-2" />
                Last Name
              </label>
              <input
                {...register('last_name')}
                type="text"
                id="last_name"
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.last_name ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={isLoading}
              />
              {errors.last_name && (
                <p className="mt-1 text-sm text-red-600">{errors.last_name.message}</p>
              )}
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                <Mail className="h-4 w-4 inline mr-2" />
                Email Address
              </label>
              <input
                {...register('email')}
                type="email"
                id="email"
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={isLoading}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            {/* Phone */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                <Phone className="h-4 w-4 inline mr-2" />
                Phone Number
              </label>
              <input
                {...register('phone')}
                type="tel"
                id="phone"
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.phone ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={isLoading}
              />
              {errors.phone && (
                <p className="mt-1 text-sm text-red-600">{errors.phone.message}</p>
              )}
            </div>
          </div>

          {/* Bio */}
          <div>
            <label htmlFor="bio" className="block text-sm font-medium text-gray-700 mb-2">
              About Me
            </label>
            <textarea
              {...register('bio')}
              id="bio"
              rows={4}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.bio ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Tell us a bit about yourself..."
              disabled={isLoading}
            />
            {errors.bio && (
              <p className="mt-1 text-sm text-red-600">{errors.bio.message}</p>
            )}
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <Button 
              type="submit"
              disabled={isLoading || !isDirty}
            >
              <Save className="h-4 w-4 mr-2" />
              {isLoading ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </div>

      {/* Notification Preferences */}
      <div className="border-b pb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          <Bell className="h-5 w-5 inline mr-2" />
          Notification Preferences
        </h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3">
            <div>
              <label className="text-sm font-medium text-gray-900">Email Notifications</label>
              <p className="text-xs text-gray-600">Receive notifications via email</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notifications.email}
                onChange={(e) => handleNotificationChange('email', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3">
            <div>
              <label className="text-sm font-medium text-gray-900">Push Notifications</label>
              <p className="text-xs text-gray-600">Receive push notifications in your browser</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notifications.push}
                onChange={(e) => handleNotificationChange('push', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3">
            <div>
              <label className="text-sm font-medium text-gray-900">SMS Notifications</label>
              <p className="text-xs text-gray-600">Receive notifications via text message</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notifications.sms}
                onChange={(e) => handleNotificationChange('sms', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Appearance */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          <Globe className="h-5 w-5 inline mr-2" />
          Appearance
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Theme</label>
            <div className="flex space-x-4">
              <button
                onClick={() => setTheme('light')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
                  theme === 'light' 
                    ? 'border-blue-500 bg-blue-50 text-blue-700' 
                    : 'border-gray-300 hover:bg-gray-50'
                }`}
              >
                <Sun className="h-4 w-4" />
                <span>Light</span>
              </button>
              <button
                onClick={() => setTheme('dark')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
                  theme === 'dark' 
                    ? 'border-blue-500 bg-blue-50 text-blue-700' 
                    : 'border-gray-300 hover:bg-gray-50'
                }`}
              >
                <Moon className="h-4 w-4" />
                <span>Dark</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GeneralSettings;