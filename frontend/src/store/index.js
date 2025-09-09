import { configureStore } from '@reduxjs/toolkit';
import { authApi } from './api/authApi';
import { apiSlice } from './api/apiSlice';
import authReducer from './slices/authSlice';
import { persistStore, persistReducer } from 'redux-persist';
import createWebStorage from 'redux-persist/lib/storage/createWebStorage';

// Create a noop storage for SSR compatibility
const createNoopStorage = () => {
  return {
    getItem(_key) {
      return Promise.resolve(null);
    },
    setItem(_key, value) {
      return Promise.resolve(value);
    },
    removeItem(_key) {
      return Promise.resolve();
    },
  };
};

// Use noop storage on server, localStorage on client for non-sensitive data only
const storage = typeof window !== 'undefined' 
  ? createWebStorage('local') 
  : createNoopStorage();

// Redux Persist Configuration
// Note: Only persist user data, not auth state or tokens for security
const persistConfig = {
  key: 'auth',
  storage,
  whitelist: ['user'], // Only persist user data - auth state recalculated on page load
};

const persistedAuthReducer = persistReducer(persistConfig, authReducer);

export const store = configureStore({
  reducer: {
    auth: persistedAuthReducer,
    [authApi.reducerPath]: authApi.reducer,
    [apiSlice.reducerPath]: apiSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [
          'persist/PERSIST', 
          'persist/REHYDRATE', 
          'persist/PAUSE',
          'persist/PURGE',
          'persist/REGISTER'
        ],
      },
    }).concat(authApi.middleware, apiSlice.middleware),
});

export const persistor = persistStore(store);

// Export types for TypeScript users (if needed later)
// export type RootState = ReturnType<typeof store.getState>;
// export type AppDispatch = typeof store.dispatch;
