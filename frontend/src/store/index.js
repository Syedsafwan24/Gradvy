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
// Persist user data and tokens with expiration validation for better UX
const persistConfig = {
  key: 'auth',
  storage,
  whitelist: ['user', 'tokens', 'isAuthenticated'], // Persist tokens with validation on load
  // Add transform to validate tokens on rehydration
  transforms: [
    {
      in: (state) => {
        // Add timestamp when storing tokens
        if (state?.tokens?.access) {
          return {
            ...state,
            tokenTimestamp: Date.now()
          };
        }
        return state;
      },
      out: (state) => {
        // Validate tokens on rehydration (max 23 hours for safety)
        if (state?.tokenTimestamp && state?.tokens?.access) {
          const tokenAge = Date.now() - state.tokenTimestamp;
          const maxAge = 23 * 60 * 60 * 1000; // 23 hours
          
          if (tokenAge > maxAge) {
            // Token too old, clear it
            return {
              ...state,
              tokens: { access: null, refresh: null },
              isAuthenticated: false,
              tokenTimestamp: null
            };
          }
        }
        return state;
      }
    }
  ]
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
