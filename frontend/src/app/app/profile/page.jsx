'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useSelector } from 'react-redux';
import { Mail, Calendar, Shield, User as UserIcon, Settings } from 'lucide-react';
import { selectCurrentUser } from '@/store/slices/authSlice';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import PageLayout from '@/components/layouts/PageLayout';
import SectionCard from '@/components/layouts/SectionCard';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

const ProfilePage = () => {
  const router = useRouter();
  const user = useSelector(selectCurrentUser);

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
    <ProtectedRoute requireAuth={true} redirectTo="/login">
      <PageLayout
        title="Profile Overview"
        description="Your account summary and key information"
        actions={
          <Button 
            onClick={() => router.push('/app/settings/account')} 
            variant="outline"
            className="h-11 gap-2"
          >
            <Settings className="w-4 h-4" />
            Edit Profile
          </Button>
        }
      >
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
          {/* Main Profile Card */}
          <div className="lg:col-span-2">
            <SectionCard title="Profile Information">
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-6">
                {/* Avatar */}
                <Avatar className="w-20 h-20 text-2xl">
                  <AvatarFallback>
                    {getInitials(user?.first_name, user?.last_name)}
                  </AvatarFallback>
                </Avatar>

                {/* User Info */}
                <div className="flex-1 min-w-0 space-y-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="text-xl sm:text-2xl font-bold">
                      {user?.first_name && user?.last_name 
                        ? `${user.first_name} ${user.last_name}` 
                        : user?.email}
                    </h2>
                    {user?.is_mfa_enabled && (
                      <Badge variant="success" className="gap-1">
                        <Shield className="w-3 h-3" />
                        2FA Enabled
                      </Badge>
                    )}
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Mail className="w-4 h-4 flex-shrink-0" />
                      <span className="truncate">{user?.email}</span>
                    </div>
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Calendar className="w-4 h-4 flex-shrink-0" />
                      <span>Member since {formatJoinDate(user?.date_joined)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </SectionCard>

            {/* Account Details */}
            <SectionCard title="Account Details" className="mt-4 sm:mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">First Name</label>
                  <p className="text-sm mt-1">{user?.first_name || 'Not set'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Last Name</label>
                  <p className="text-sm mt-1">{user?.last_name || 'Not set'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Username</label>
                  <p className="text-sm mt-1">{user?.username || user?.email}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Email Verified</label>
                  <p className="text-sm mt-1">
                    <Badge variant={user?.is_email_verified ? 'success' : 'secondary'}>
                      {user?.is_email_verified ? 'Verified' : 'Not Verified'}
                    </Badge>
                  </p>
                </div>
              </div>
            </SectionCard>
          </div>

          {/* Sidebar */}
          <div className="space-y-4 sm:space-y-6">
            {/* Quick Stats */}
            <SectionCard title="Quick Stats">
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <span className="text-sm text-muted-foreground">Account Status</span>
                  <Badge variant="success">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <span className="text-sm text-muted-foreground">Security</span>
                  <Badge variant={user?.is_mfa_enabled ? 'success' : 'warning'}>
                    {user?.is_mfa_enabled ? 'Protected' : 'Basic'}
                  </Badge>
                </div>
              </div>
            </SectionCard>

            {/* Quick Actions */}
            <SectionCard title="Quick Actions">
              <div className="space-y-2">
                <Button 
                  variant="outline" 
                  className="w-full justify-start h-11 gap-2"
                  onClick={() => router.push('/app/settings/account')}
                >
                  <UserIcon className="w-4 h-4" />
                  Edit Account
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start h-11 gap-2"
                  onClick={() => router.push('/app/settings/security')}
                >
                  <Shield className="w-4 h-4" />
                  Security Settings
                </Button>
              </div>
            </SectionCard>
          </div>
        </div>
      </PageLayout>
    </ProtectedRoute>
  );
};

export default ProfilePage;