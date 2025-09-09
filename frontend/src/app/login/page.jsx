'use client';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Eye, EyeOff, Mail, Lock, Loader2 } from 'lucide-react';
import { useLoginMutation, useVerifyMFAMutation } from '../../store/api/authApi';
import { useSelector } from 'react-redux';
import { selectIsAuthenticated, selectAuthError } from '../../store/slices/authSlice';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import toast from 'react-hot-toast';

// Validation schema
const loginSchema = yup.object({
  email: yup
    .string()
    .email('Please enter a valid email')
    .required('Email is required'),
  password: yup
    .string()
    .required('Password is required'),
  remember_me: yup.boolean().default(false),
});

const mfaSchema = yup.object({
  code: yup
    .string()
    .matches(/^\d{6}$/, 'MFA code must be 6 digits')
    .required('MFA code is required'),
});

const LoginPage = () => {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [mfaRequired, setMfaRequired] = useState(false);
  const [mfaToken, setMfaToken] = useState('');
  const [formsReady, setFormsReady] = useState(false);
  
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const authError = useSelector(selectAuthError);
  
  const [login, { isLoading: isLoginLoading }] = useLoginMutation();
  const [verifyMFA, { isLoading: isMFALoading }] = useVerifyMFAMutation();

  // Login form
  const {
    register: registerLogin,
    handleSubmit: handleLoginSubmit,
    formState: { errors: loginErrors },
    reset: resetLogin,
  } = useForm({
    resolver: yupResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      remember_me: false,
    },
  });

  // MFA form
  const {
    register: registerMFA,
    handleSubmit: handleMFASubmit,
    formState: { errors: mfaErrors },
    reset: resetMFA,
    watch: watchMFA,
    setValue: setMFAValue,
  } = useForm({
    resolver: yupResolver(mfaSchema),
    defaultValues: {
      code: '',
    },
  });

  const mfaCodeValue = watchMFA('code') || '';
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const [isInputFocused, setIsInputFocused] = useState(false);

  // Handle MFA code input formatting
  const handleMFACodeChange = (e) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 6);
    setMFAValue('code', value, { shouldValidate: true });
  };

  // Handle input focus
  const handleInputFocus = () => {
    setIsInputFocused(true);
    setFocusedIndex(mfaCodeValue.length);
  };

  // Handle input blur
  const handleInputBlur = () => {
    setIsInputFocused(false);
    setFocusedIndex(-1);
  };

  // Initialize forms and redirect if authenticated
  useEffect(() => {
    // Mark forms as ready after initial render
    setFormsReady(true);
    
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const onLoginSubmit = async (data) => {
    try {
      const result = await login(data).unwrap();
      
      if (result.mfa_required) {
        setMfaRequired(true);
        setMfaToken(result.mfa_token);
        toast.success('Please enter your MFA code');
      } else {
        toast.success('Login successful!');
        router.push('/dashboard');
      }
    } catch (error) {
      console.error('Login error:', error);
      toast.error(error?.data?.detail || error?.data?.message || 'Login failed. Please try again.');
    }
  };

  const onMFASubmit = async (data) => {
    try {
      await verifyMFA({
        code: data.code,
        mfa_token: mfaToken,
      }).unwrap();
      
      toast.success('Login successful!');
      router.push('/dashboard');
    } catch (error) {
      console.error('MFA error:', error);
      toast.error(error?.data?.error || 'Invalid MFA code. Please try again.');
    }
  };

  const handleBackToLogin = () => {
    setMfaRequired(false);
    setMfaToken('');
    resetMFA();
  };

  // Show loading until forms are ready
  if (!formsReady) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (mfaRequired) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          <Card className="p-8 shadow-2xl">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Two-Factor Authentication
              </h1>
              <p className="text-gray-600">
                Please enter the 6-digit code from your authenticator app
              </p>
            </div>

            <form onSubmit={handleMFASubmit(onMFASubmit)} className="space-y-6">
              <div>
                <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-4 text-center">
                  Authentication Code
                </label>
                
                {/* Enhanced Visual Code Input Boxes with Focus States */}
                <div className="relative mb-6">
                  <div className="flex justify-center space-x-3 sm:space-x-4">
                    {Array.from({ length: 6 }).map((_, index) => {
                      const isCurrentFocus = isInputFocused && index === mfaCodeValue.length && index < 6;
                      const isFilled = index < mfaCodeValue.length;
                      const hasError = mfaErrors.code;
                      
                      return (
                        <div
                          key={index}
                          className={`
                            relative w-12 h-12 sm:w-14 sm:h-14 border-2 rounded-xl 
                            flex items-center justify-center text-xl sm:text-2xl font-mono font-bold
                            transition-all duration-300 ease-in-out transform
                            ${hasError
                              ? 'border-red-400 bg-red-50 text-red-700 shadow-red-100'
                              : isFilled
                              ? 'border-green-500 bg-green-50 text-green-800 shadow-green-100 scale-105'
                              : isCurrentFocus
                              ? 'border-blue-500 bg-blue-50 text-blue-900 shadow-blue-200 ring-2 ring-blue-200 scale-105'
                              : 'border-gray-300 bg-gray-50 text-gray-500 hover:border-gray-400 hover:bg-gray-100'
                            }
                            ${(isFilled || isCurrentFocus) ? 'shadow-lg' : 'shadow-sm'}
                          `}
                        >
                          {/* Digit Display */}
                          <span className={`
                            transition-all duration-200
                            ${isFilled ? 'opacity-100 scale-100' : 'opacity-0 scale-75'}
                          `}>
                            {mfaCodeValue[index] || ''}
                          </span>
                          
                          {/* Focus Indicator Cursor */}
                          {isCurrentFocus && (
                            <div className="absolute inset-0 flex items-center justify-center">
                              <div className="w-0.5 h-6 bg-blue-500 animate-pulse rounded-full" />
                            </div>
                          )}
                          
                          {/* Success Check Animation */}
                          {isFilled && !hasError && (
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                              <div className="w-2 h-1 bg-white rounded-full" />
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  {/* Enhanced Transparent Functional Input Field */}
                  <input
                    {...registerMFA('code')}
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    id="code"
                    placeholder=""
                    maxLength={6}
                    value={mfaCodeValue}
                    onChange={handleMFACodeChange}
                    onFocus={handleInputFocus}
                    onBlur={handleInputBlur}
                    autoFocus
                    autoComplete="one-time-code"
                    className="absolute inset-0 w-full h-full opacity-0 text-center text-2xl tracking-widest z-10 cursor-text"
                    style={{ letterSpacing: '3rem' }}
                  />
                  
                  {/* Progress Indicator */}
                  <div className="mt-4 flex justify-center">
                    <div className="flex space-x-1">
                      {Array.from({ length: 6 }).map((_, index) => (
                        <div
                          key={index}
                          className={`
                            w-2 h-2 rounded-full transition-all duration-300
                            ${index < mfaCodeValue.length
                              ? 'bg-green-500 scale-110'
                              : index === mfaCodeValue.length && isInputFocused
                              ? 'bg-blue-500 animate-pulse'
                              : 'bg-gray-300'
                            }
                          `}
                        />
                      ))}
                    </div>
                  </div>
                </div>
                
                {/* Enhanced Instructions */}
                <div className="text-center space-y-3">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <p className="text-sm text-blue-800 font-medium">
                      📱 Enter the 6-digit code from your authenticator app
                    </p>
                    <p className="text-xs text-blue-600 mt-1">
                      Code changes every 30 seconds
                    </p>
                  </div>
                  
                  {/* Live Status Indicator */}
                  {mfaCodeValue.length > 0 && (
                    <div className="flex items-center justify-center space-x-2 text-sm">
                      <div className={`
                        w-2 h-2 rounded-full
                        ${mfaCodeValue.length === 6 
                          ? 'bg-green-500 animate-pulse' 
                          : 'bg-blue-500 animate-pulse'
                        }
                      `} />
                      <span className={`
                        font-medium
                        ${mfaCodeValue.length === 6 ? 'text-green-700' : 'text-blue-700'}
                      `}>
                        {mfaCodeValue.length === 6 
                          ? 'Ready to verify' 
                          : `${mfaCodeValue.length} of 6 digits entered`
                        }
                      </span>
                    </div>
                  )}
                </div>

                {/* Enhanced Error Display */}
                {mfaErrors.code && (
                  <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-center">
                    <p className="text-sm text-red-700 font-medium">❌ {mfaErrors.code.message}</p>
                    <p className="text-xs text-red-600 mt-1">Please check your authenticator app and try again</p>
                  </div>
                )}
              </div>

              <Button
                type="submit"
                disabled={isMFALoading}
                className="w-full"
              >
                {isMFALoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  'Verify Code'
                )}
              </Button>

              <Button
                type="button"
                variant="outline"
                onClick={handleBackToLogin}
                className="w-full"
              >
                Back to Login
              </Button>
            </form>
          </Card>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-2xl"
      >
        <Card className="p-8 shadow-2xl">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h1>
            <p className="text-gray-600">Please sign in to your account</p>
          </div>

          <form onSubmit={handleLoginSubmit(onLoginSubmit)} className="space-y-6">
            {/* Email & Password - stacked */}
            <div className="grid grid-cols-1 gap-6">
              {/* Email Field */}
              <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  {...registerLogin('email')}
                  type="email"
                  id="email"
                  placeholder="Enter your email"
                  className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                    loginErrors.email ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
              </div>
              {loginErrors.email && (
                <p className="mt-1 text-sm text-red-600">{loginErrors.email.message}</p>
              )}
              </div>

              {/* Password Field */}
              <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  {...registerLogin('password')}
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  placeholder="Enter your password"
                  className={`w-full pl-10 pr-12 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                    loginErrors.password ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
              {loginErrors.password && (
                <p className="mt-1 text-sm text-red-600">{loginErrors.password.message}</p>
              )}
              </div>
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  {...registerLogin('remember_me')}
                  type="checkbox"
                  id="remember_me"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="remember_me" className="ml-2 block text-sm text-gray-700">
                  Remember me
                </label>
              </div>
              <Link
                href="/forgot-password"
                className="text-sm text-blue-600 hover:text-blue-500"
              >
                Forgot password?
              </Link>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={isLoginLoading}
              className="w-full"
            >
              {isLoginLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>

            {/* Forgot Password Link */}
            <div className="text-center">
              <Link href="/forgot-password" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                Forgot your password?
              </Link>
            </div>

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Don't have an account?</span>
              </div>
            </div>

            {/* Sign Up Link */}
            <Link href="/register">
              <Button variant="outline" className="w-full">
                Create Account
              </Button>
            </Link>

            {/* Future: Social Login Placeholder */}
            <div className="text-center text-sm text-gray-500">
              <p>Social login options coming soon</p>
            </div>
          </form>
        </Card>
      </motion.div>
    </div>
  );
};

export default LoginPage;
