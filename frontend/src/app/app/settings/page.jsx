'use client';

import React from 'react';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/slices/authSlice';
import GeneralSettings from '@/components/settings/GeneralSettings';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import PageLayout from '@/components/layouts/PageLayout';
import SectionCard from '@/components/layouts/SectionCard';

const SettingsPage = () => {
  const user = useSelector(selectCurrentUser);

  return (
    <ProtectedRoute requireAuth={true} redirectTo="/login">
      <PageLayout
        title="General Settings"
        description="Manage your basic account preferences and settings"
      >
        <SectionCard>
          <GeneralSettings user={user} />
        </SectionCard>
      </PageLayout>
    </ProtectedRoute>
  );
};

export default SettingsPage;