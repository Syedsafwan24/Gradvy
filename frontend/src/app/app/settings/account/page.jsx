'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/slices/authSlice';
import AccountSettings from '@/components/settings/AccountSettings';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import PageLayout from '@/components/layouts/PageLayout';
import SectionCard from '@/components/layouts/SectionCard';

const AccountSettingsPage = () => {
  const user = useSelector(selectCurrentUser);

  return (
    <ProtectedRoute requireAuth={true} redirectTo="/login">
      <PageLayout
        title="Account Settings"
        description="Manage your account and subscription settings"
      >
        <SectionCard>
          <AccountSettings user={user} />
        </SectionCard>
      </PageLayout>
    </ProtectedRoute>
  );
};

export default AccountSettingsPage;