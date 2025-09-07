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
    .matches(/^\\d{6}$/, 'MFA code must be 6 digits')
    .required('MFA code is required'),
});

const LoginPage = () => {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [mfaRequired, setMfaRequired] = useState(false);
  const [mfaToken, setMfaToken] = useState('');
  
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
  } = useForm({
    resolver: yupResolver(mfaSchema),
    defaultValues: {
      code: '',
    },
  });

  // Redirect if already authenticated
  useEffect(() => {
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
                <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-2">
                  Authentication Code
                </label>
                <input
                  {...registerMFA('code')}
                  type="text"
                  id="code"
                  placeholder="000000"
                  maxLength={6}
                  className={`w-full px-4 py-3 text-center text-lg tracking-widest border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${ 
                    mfaErrors.code ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {mfaErrors.code && (
                  <p className="mt-1 text-sm text-red-600">{mfaErrors.code.message}</p>
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
        className="w-full max-w-md"
      >
        <Card className="p-8 shadow-2xl">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h1>
            <p className="text-gray-600">Please sign in to your account</p>
          </div>

          <form onSubmit={handleLoginSubmit(onLoginSubmit)} className="space-y-6">
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
