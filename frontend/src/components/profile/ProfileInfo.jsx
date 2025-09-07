'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Edit, Save, X, User, Mail, Phone, MapPin, Calendar } from 'lucide-react';
import { useUpdateProfileMutation } from '../../store/api/authApi';
import { Button } from '../ui/Button';
import toast from 'react-hot-toast';

const profileSchema = yup.object({
  first_name: yup.string().required('First name is required'),
  last_name: yup.string().required('Last name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  phone: yup.string().nullable(),
  bio: yup.string().max(500, 'Bio must be less than 500 characters').nullable(),
});

const ProfileInfo = ({ user }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [updateProfile, { isLoading }] = useUpdateProfileMutation();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty }
  } = useForm({
    resolver: yupResolver(profileSchema),
    defaultValues: {
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      email: user.email || '',
      phone: user.phone || '',
      bio: user.bio || '',
    }
  });

  const handleEdit = () => {
    setIsEditing(true);
    reset({
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      email: user.email || '',
      phone: user.phone || '',
      bio: user.bio || '',
    });
  };

  const handleCancel = () => {
    setIsEditing(false);
    reset();
  };

  const onSubmit = async (data) => {
    try {
      await updateProfile(data).unwrap();
      setIsEditing(false);
      toast.success('Profile updated successfully!');
    } catch (error) {
      console.error('Profile update failed:', error);
      toast.error('Failed to update profile. Please try again.');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not specified';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return 'Not specified';
    }
  };

  return (
    <div className="space-y-6">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Personal Information</h3>
          <p className="text-sm text-gray-600">Update your personal details and information</p>
        </div>
        {!isEditing ? (
          <Button variant="outline" size="sm" onClick={handleEdit}>
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
        ) : (
          <div className="flex space-x-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleCancel}
              disabled={isLoading}
            >
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
            <Button 
              size="sm" 
              onClick={handleSubmit(onSubmit)}
              disabled={isLoading || !isDirty}
            >
              <Save className="h-4 w-4 mr-2" />
              {isLoading ? 'Saving...' : 'Save'}
            </Button>
          </div>
        )}
      </div>

      {/* Profile Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* First Name */}
          <div>
            <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-2">
              <User className="h-4 w-4 inline mr-2" />
              First Name
            </label>
            {isEditing ? (
              <div>
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
            ) : (
              <p className="py-2 px-3 bg-gray-50 rounded-lg text-gray-900">
                {user.first_name || 'Not specified'}
              </p>
            )}
          </div>

          {/* Last Name */}
          <div>
            <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-2">
              <User className="h-4 w-4 inline mr-2" />
              Last Name
            </label>
            {isEditing ? (
              <div>
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
            ) : (
              <p className="py-2 px-3 bg-gray-50 rounded-lg text-gray-900">
                {user.last_name || 'Not specified'}
              </p>
            )}
          </div>

          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              <Mail className="h-4 w-4 inline mr-2" />
              Email Address
            </label>
            {isEditing ? (
              <div>
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
            ) : (
              <p className="py-2 px-3 bg-gray-50 rounded-lg text-gray-900">
                {user.email}
              </p>
            )}
          </div>

          {/* Phone */}
          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
              <Phone className="h-4 w-4 inline mr-2" />
              Phone Number
            </label>
            {isEditing ? (
              <div>
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
            ) : (
              <p className="py-2 px-3 bg-gray-50 rounded-lg text-gray-900">
                {user.phone || 'Not specified'}
              </p>
            )}
          </div>
        </div>

        {/* Bio */}
        <div>
          <label htmlFor="bio" className="block text-sm font-medium text-gray-700 mb-2">
            About Me
          </label>
          {isEditing ? (
            <div>
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
          ) : (
            <p className="py-2 px-3 bg-gray-50 rounded-lg text-gray-900 min-h-[100px]">
              {user.bio || 'No bio added yet'}
            </p>
          )}
        </div>

        {/* Account Info */}
        <div className="border-t pt-6">
          <h4 className="text-md font-medium text-gray-900 mb-4">Account Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="block text-sm font-medium text-gray-700 mb-1">
                <Calendar className="h-4 w-4 inline mr-2" />
                Member Since
              </span>
              <p className="text-gray-900">{formatDate(user.date_joined)}</p>
            </div>
            <div>
              <span className="block text-sm font-medium text-gray-700 mb-1">
                Last Updated
              </span>
              <p className="text-gray-900">{formatDate(user.updated_at)}</p>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ProfileInfo;