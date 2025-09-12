import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  user: null,
  tokens: {
    access: null,
    refresh: null,
  },
  isAuthenticated: false,
  isLoading: false,
  error: null,
  tokenTimestamp: null, // Track when tokens were stored for validation
  // MFA state management
  mfa: {
    isEnrolling: false,
    currentStep: 0,
    qrCode: null,
    secret: null,
    backupCodes: [],
    isDisabling: false,
    enrollmentData: null,
  },
  // Password reset state
  passwordReset: {
    isRequesting: false,
    resetEmail: null,
    isResetting: false,
  },
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (state, action) => {
      const { user, tokens, access, refresh } = action.payload;
      state.user = user;
      
      // Handle both new structure (tokens object) and legacy structure (direct access/refresh)
      if (tokens) {
        state.tokens = {
          access: tokens.access || null,
          refresh: tokens.refresh || null,
        };
      } else {
        state.tokens = {
          access: access || null,
          refresh: refresh || null,
        };
      }
      
      // Set timestamp when storing new tokens for persistence validation
      if (state.tokens.access) {
        state.tokenTimestamp = Date.now();
      }
      
      // Only set authenticated if we have a valid access token
      state.isAuthenticated = !!(state.tokens.access && state.user);
      state.error = null;
      
    },
    logout: (state) => {
      state.user = null;
      state.tokens = {
        access: null,
        refresh: null, // Refresh token is now in httpOnly cookies
      };
      state.isAuthenticated = false;
      state.error = null;
      state.tokenTimestamp = null;
      
      // Clear any auth-related cookies that can be cleared from JS
      // Note: httpOnly cookies (refresh_token) will be cleared by the backend
      try {
        const { clearAuthCookies } = require('../../lib/cookieUtils');
        clearAuthCookies();
      } catch (error) {
        console.warn('Failed to clear auth cookies:', error);
      }
    },
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    clearError: (state) => {
      state.error = null;
    },
    updateUser: (state, action) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
    setAccessToken: (state, action) => {
      state.tokens.access = action.payload;
      // Update isAuthenticated based on token presence
      state.isAuthenticated = !!(state.tokens.access && state.user);
    },
    // MFA reducers
    setMFAEnrollmentData: (state, action) => {
      state.mfa.enrollmentData = action.payload;
      state.mfa.qrCode = action.payload?.qr_code || null;
      state.mfa.secret = action.payload?.secret || null;
      state.mfa.backupCodes = action.payload?.backup_codes || [];
    },
    setMFAEnrolling: (state, action) => {
      state.mfa.isEnrolling = action.payload;
    },
    setMFACurrentStep: (state, action) => {
      state.mfa.currentStep = action.payload;
    },
    setMFADisabling: (state, action) => {
      state.mfa.isDisabling = action.payload;
    },
    setMFABackupCodes: (state, action) => {
      state.mfa.backupCodes = action.payload || [];
    },
    clearMFAData: (state) => {
      state.mfa = {
        isEnrolling: false,
        currentStep: 0,
        qrCode: null,
        secret: null,
        backupCodes: [],
        isDisabling: false,
        enrollmentData: null,
      };
    },
    // Password reset reducers
    setPasswordResetRequesting: (state, action) => {
      state.passwordReset.isRequesting = action.payload;
    },
    setPasswordResetEmail: (state, action) => {
      state.passwordReset.resetEmail = action.payload;
    },
    setPasswordResetting: (state, action) => {
      state.passwordReset.isResetting = action.payload;
    },
    clearPasswordResetData: (state) => {
      state.passwordReset = {
        isRequesting: false,
        resetEmail: null,
        isResetting: false,
      };
    },
    // Authentication initialization
    initializeAuth: (state) => {
      // Reset auth state on initialization - tokens will be fetched from cookies if valid
      state.isAuthenticated = false;
      state.tokens = {
        access: null,
        refresh: null,
      };
      state.tokenTimestamp = null;
      state.error = null;
    },
  },
});

export const {
  setCredentials,
  logout,
  setLoading,
  setError,
  clearError,
  updateUser,
  setAccessToken,
  initializeAuth,
  // MFA actions
  setMFAEnrollmentData,
  setMFAEnrolling,
  setMFACurrentStep,
  setMFADisabling,
  setMFABackupCodes,
  clearMFAData,
  // Password reset actions
  setPasswordResetRequesting,
  setPasswordResetEmail,
  setPasswordResetting,
  clearPasswordResetData,
} = authSlice.actions;

export default authSlice.reducer;

// Selectors
export const selectCurrentUser = (state) => state.auth.user;
export const selectIsAuthenticated = (state) => state.auth.isAuthenticated;
export const selectAccessToken = (state) => state.auth.tokens?.access;
export const selectRefreshToken = (state) => state.auth.tokens?.refresh;
export const selectAuthTokens = (state) => state.auth.tokens;
export const selectAuthLoading = (state) => state.auth.isLoading;
export const selectAuthError = (state) => state.auth.error;

// MFA selectors
export const selectMFAState = (state) => state.auth.mfa;
export const selectMFAIsEnrolling = (state) => state.auth.mfa.isEnrolling;
export const selectMFACurrentStep = (state) => state.auth.mfa.currentStep;
export const selectMFAQRCode = (state) => state.auth.mfa.qrCode;
export const selectMFASecret = (state) => state.auth.mfa.secret;
export const selectMFABackupCodes = (state) => state.auth.mfa.backupCodes;
export const selectMFAIsDisabling = (state) => state.auth.mfa.isDisabling;
export const selectMFAEnrollmentData = (state) => state.auth.mfa.enrollmentData;

// Password reset selectors
export const selectPasswordResetState = (state) => state.auth.passwordReset;
export const selectPasswordResetIsRequesting = (state) => state.auth.passwordReset.isRequesting;
export const selectPasswordResetEmail = (state) => state.auth.passwordReset.resetEmail;
export const selectPasswordResetIsResetting = (state) => state.auth.passwordReset.isResetting;

// Token validation selectors
export const selectTokenTimestamp = (state) => state.auth.tokenTimestamp;

// Helper selector to check if current tokens are valid and not expired
export const selectAreTokensValid = (state) => {
  const { tokens, tokenTimestamp, user } = state.auth;
  
  // Must have access token and user
  if (!tokens?.access || !user) {
    return false;
  }
  
  // Check token age if timestamp exists
  if (tokenTimestamp) {
    const tokenAge = Date.now() - tokenTimestamp;
    const maxAge = 23 * 60 * 60 * 1000; // 23 hours
    
    if (tokenAge > maxAge) {
      return false;
    }
  }
  
  return true;
};

// Helper selector to check if tokens need refresh
export const selectShouldRefreshTokens = (state) => {
  const { tokens, tokenTimestamp, user } = state.auth;
  
  // If no access token but we have user, should try to refresh
  if (!tokens?.access && user) {
    return true;
  }
  
  // If token is getting old (20+ hours), should refresh
  if (tokenTimestamp && tokens?.access) {
    const tokenAge = Date.now() - tokenTimestamp;
    const refreshThreshold = 20 * 60 * 60 * 1000; // 20 hours
    
    if (tokenAge > refreshThreshold) {
      return true;
    }
  }
  
  return false;
};

// Computed selectors
export const selectUserMFAEnabled = (state) => state.auth.user?.mfa_enrolled || false;
