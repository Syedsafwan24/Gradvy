'use client';

import React from 'react';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { store, persistor } from '../store';
import AuthInitializer from '../components/auth/AuthInitializer';

const ReduxProvider = ({ children }) => {
  return (
    <Provider store={store}>
      <PersistGate loading={<div>Loading...</div>} persistor={persistor}>
        <AuthInitializer>
          {children}
        </AuthInitializer>
      </PersistGate>
    </Provider>
  );
};

export default ReduxProvider;
