'use client';

import React from 'react';
import { User, Shield, Mail, Calendar } from 'lucide-react';
import { Button } from '../ui/Button';

const ProfileHeader = ({ user }) => {
  const getInitials = (firstName, lastName) => {
    return `${firstName?.charAt(0) || ''}${lastName?.charAt(0) || ''}`.toUpperCase();
  };

  const formatJoinDate = (dateString) => {
    if (!dateString) return 'Recently';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long'
      });
    } catch {
      return 'Recently';
    }
  };

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-6">
      {/* Profile Picture/Avatar */}
      <div className="flex-shrink-0">
        <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center">
          <span className="text-2xl font-bold text-white">
            {getInitials(user.first_name, user.last_name)}
          </span>
        </div>
      </div>

      {/* User Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center space-x-3 mb-2">
          <h2 className="text-2xl font-bold text-gray-900">
            {user.first_name && user.last_name 
              ? `${user.first_name} ${user.last_name}` 
              : user.email}
          </h2>
          {user.is_mfa_enabled && (
            <div className="flex items-center space-x-1 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
              <Shield className="h-3 w-3" />
              <span>2FA</span>
            </div>
          )}
        </div>
        
        <div className="space-y-1 text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <Mail className="h-4 w-4" />
            <span>{user.email}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Calendar className="h-4 w-4" />
            <span>Member since {formatJoinDate(user.date_joined)}</span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex-shrink-0">
        <Button variant="outline" size="sm">
          Edit Profile
        </Button>
      </div>
    </div>
  );
};

export default ProfileHeader;