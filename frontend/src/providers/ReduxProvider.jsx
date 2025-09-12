'use client';

import React from 'react';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { store, persistor } from '../store';
import AuthInitializer from '../components/auth/AuthInitializer';

// Enhanced loading component for PersistGate
const PersistLoading = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="text-center space-y-4">
      <div className="relative">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600 mx-auto"></div>
      </div>
      <div className="space-y-2">
        <p className="text-lg font-medium text-gray-900">Loading Gradvy</p>
        <p className="text-sm text-gray-600">Preparing your workspace...</p>
      </div>
    </div>
  </div>
);

const ReduxProvider = ({ children }) => {
  return (
    <Provider store={store}>
      <PersistGate loading={<PersistLoading />} persistor={persistor}>
        <AuthInitializer>
          {children}
        </AuthInitializer>
      </PersistGate>
    </Provider>
  );
};

export default ReduxProvider;
