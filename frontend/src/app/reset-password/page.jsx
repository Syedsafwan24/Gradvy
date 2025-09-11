'use client';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Eye, EyeOff, Lock, ArrowLeft, Loader2, CheckCircle } from 'lucide-react';
import { useConfirmPasswordResetMutation } from '@/store/api/authApi';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import toast from 'react-hot-toast';

// Validation schema
const resetSchema = yup.object({
  new_password: yup
    .string()
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    )
    .required('New password is required'),
  new_password_confirm: yup
    .string()
    .oneOf([yup.ref('new_password'), null], 'Passwords must match')
    .required('Please confirm your password'),
});

const ResetPasswordPage = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [token, setToken] = useState('');
  const [isTokenValid, setIsTokenValid] = useState(null);
  const [resetSuccess, setResetSuccess] = useState(false);
  
  const [confirmReset, { isLoading }] = useConfirmPasswordResetMutation();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: yupResolver(resetSchema),
    defaultValues: {
      new_password: '',
      new_password_confirm: '',
    },
  });

  // Extract token from URL parameters on component mount
  useEffect(() => {
    const tokenParam = searchParams.get('token');
    if (tokenParam) {
      setToken(tokenParam);
      setIsTokenValid(true);
    } else {
      setIsTokenValid(false);
      toast.error('Invalid reset link. Please request a new password reset.');
    }
  }, [searchParams]);

  const onSubmit = async (data) => {
    if (!token) {
      toast.error('Invalid reset token');
      return;
    }

    try {
      await confirmReset({
        token: token,
        new_password: data.new_password,
        new_password_confirm: data.new_password_confirm,
      }).unwrap();
      
      setResetSuccess(true);
      toast.success('Password reset successfully!');
    } catch (error) {
      console.error('Password reset error:', error);
      
      // Handle specific error cases
      if (error?.data?.token) {
        toast.error('Reset link has expired or is invalid. Please request a new password reset.');
        setIsTokenValid(false);
      } else if (error?.data?.new_password) {
        toast.error('Password requirements not met. Please check the requirements.');
      } else {
        toast.error(error?.data?.message || 'Failed to reset password. Please try again.');
      }
    }
  };

  // Show success message after password reset
  if (resetSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          <Card className="p-8 shadow-2xl text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Password Reset Successful
            </h1>
            
            <p className="text-gray-600 mb-6">
              Your password has been successfully updated. You can now login with your new password.
            </p>
            
            <Link href="/login">
              <Button className="w-full">
                Continue to Login
              </Button>
            </Link>
          </Card>
        </motion.div>
      </div>
    );
  }

  // Show error if token is invalid
  if (isTokenValid === false) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          <Card className="p-8 shadow-2xl text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Lock className="h-8 w-8 text-red-600" />
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Invalid Reset Link
            </h1>
            
            <p className="text-gray-600 mb-6">
              This password reset link is invalid or has expired. Please request a new password reset.
            </p>
            
            <div className="space-y-3">
              <Link href="/forgot-password">
                <Button className="w-full">
                  Request New Reset
                </Button>
              </Link>
              
              <Link href="/login">
                <Button variant="outline" className="w-full">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Login
                </Button>
              </Link>
            </div>
          </Card>
        </motion.div>
      </div>
    );
  }

  // Show loading while validating token
  if (isTokenValid === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Validating reset link...</p>
        </div>
      </div>
    );
  }

  // Main reset password form
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Reset Password</h1>
            <p className="text-gray-600">
              Enter your new password below
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* New Password Field */}
            <div>
              <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 mb-2">
                New Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  {...register('new_password')}
                  type={showPassword ? 'text' : 'password'}
                  id="new_password"
                  placeholder="Enter new password"
                  className={`w-full pl-10 pr-12 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                    errors.new_password ? 'border-red-500' : 'border-gray-300'
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
              {errors.new_password && (
                <p className="mt-1 text-sm text-red-600">{errors.new_password.message}</p>
              )}
            </div>

            {/* Confirm Password Field */}
            <div>
              <label htmlFor="new_password_confirm" className="block text-sm font-medium text-gray-700 mb-2">
                Confirm New Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  {...register('new_password_confirm')}
                  type={showConfirmPassword ? 'text' : 'password'}
                  id="new_password_confirm"
                  placeholder="Confirm new password"
                  className={`w-full pl-10 pr-12 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                    errors.new_password_confirm ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
              {errors.new_password_confirm && (
                <p className="mt-1 text-sm text-red-600">{errors.new_password_confirm.message}</p>
              )}
            </div>

            {/* Password Requirements */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Password Requirements:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>" At least 8 characters long</li>
                <li>" Contains uppercase and lowercase letters</li>
                <li>" Contains at least one number</li>
              </ul>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Resetting password...
                </>
              ) : (
                'Reset Password'
              )}
            </Button>

            {/* Back to Login */}
            <div className="text-center">
              <Link
                href="/login"
                className="text-sm text-blue-600 hover:text-blue-500 flex items-center justify-center"
              >
                <ArrowLeft className="h-4 w-4 mr-1" />
                Back to Login
              </Link>
            </div>
          </form>
        </Card>
      </motion.div>
    </div>
  );
};

export default ResetPasswordPage;