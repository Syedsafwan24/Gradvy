'use client';

import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Shield, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { selectMFAEnrollmentData } from '@/store/slices/authSlice';
import { useConfirmMFAEnrollmentMutation } from '@/store/api/authApi';
import toast from 'react-hot-toast';

// Validation schema
const verificationSchema = yup.object({
  code: yup
    .string()
    .matches(/^\d{6}$/, 'Code must be 6 digits')
    .required('Verification code is required'),
});

const TOTPVerificationStep = ({ onNext, onPrevious, onStepComplete }) => {
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationComplete, setVerificationComplete] = useState(false);
  const enrollmentData = useSelector(selectMFAEnrollmentData);
  const [confirmMFAEnrollment] = useConfirmMFAEnrollmentMutation();

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
  } = useForm({
    resolver: yupResolver(verificationSchema),
    defaultValues: {
      code: '',
    },
  });

  const codeValue = watch('code');

  // Handle input formatting (only digits, max 6 characters)
  const handleCodeChange = (e) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 6);
    setValue('code', value, { shouldValidate: true });
  };

  const verifyCode = async () => {
    if (!enrollmentData?.device_id) {
      toast.error('MFA setup data not found. Please start over.');
      return false;
    }

    if (codeValue.length !== 6) {
      toast.error('Please enter a complete 6-digit code.');
      return false;
    }

    setIsVerifying(true);
    
    try {
      await confirmMFAEnrollment({ 
        device_id: enrollmentData.device_id, 
        code: codeValue 
      }).unwrap();
      
      toast.success('Code verified successfully!');
      setVerificationComplete(true);
      onStepComplete?.();
      return true;
    } catch (error) {
      console.error('TOTP verification failed:', error);
      const errorMessage = error?.data?.error || 'Invalid code. Please try again.';
      toast.error(errorMessage);
      return false;
    } finally {
      setIsVerifying(false);
    }
  };

  // Auto-verify when 6 digits are entered
  useEffect(() => {
    if (codeValue.length === 6 && !verificationComplete && !isVerifying) {
      verifyCode();
    }
  }, [codeValue, verificationComplete, isVerifying]);

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Shield className="h-8 w-8 text-green-600" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Verify Your Setup</h3>
        <p className="text-gray-600">
          Enter the 6-digit code from your authenticator app to complete the setup.
        </p>
      </div>

      <div className="space-y-6">
        <div>
          <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-2">
            Authentication Code
          </label>
          <div className="flex justify-center">
            <input
              {...register('code')}
              type="text"
              id="code"
              placeholder="000000"
              maxLength={6}
              onChange={handleCodeChange}
              value={codeValue || ''}
              className={`
                w-48 px-4 py-3 text-center text-2xl font-mono tracking-widest
                border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                transition-colors ${errors.code ? 'border-red-500' : 'border-gray-300'}
              `}
              disabled={isVerifying || verificationComplete}
              autoFocus
            />
          </div>
          {errors.code && (
            <p className="mt-2 text-sm text-red-600 text-center">{errors.code.message}</p>
          )}
        </div>

        {/* Enhanced Visual Code Input */}
        <div className="flex justify-center space-x-2">
          {Array.from({ length: 6 }).map((_, index) => (
            <div
              key={index}
              className={`
                w-12 h-14 border-2 rounded-xl flex items-center justify-center
                text-xl font-mono font-bold transition-all duration-300
                ${verificationComplete
                  ? 'border-green-500 bg-green-50 text-green-900'
                  : index < codeValue.length 
                  ? 'border-blue-500 bg-blue-50 text-blue-900' 
                  : 'border-gray-300 bg-gray-50 text-gray-400'
                }
              `}
            >
              {codeValue[index] || ''}
              {verificationComplete && index === 5 && (
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                  <div className="w-2 h-1 bg-white rounded-full" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Status Indicator */}
        {isVerifying && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center space-x-2">
              <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
              <p className="text-blue-800 font-medium">Verifying code...</p>
            </div>
          </div>
        )}

        {verificationComplete && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                <div className="w-3 h-1.5 bg-white rounded-full" />
              </div>
              <p className="text-green-800 font-medium">Code verified successfully!</p>
            </div>
            <p className="text-green-700 text-sm">Click Continue to proceed with backup codes.</p>
          </div>
        )}

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 className="font-semibold text-yellow-800 mb-2">Tips for getting your code:</h4>
          <ul className="text-sm text-yellow-700 space-y-1">
            <li>• Open your authenticator app</li>
            <li>• Find the "Gradvy" or similar account you just added</li>
            <li>• Enter the current 6-digit code (it updates every 30 seconds)</li>
            <li>• Make sure to enter the code before it expires</li>
          </ul>
        </div>
      </div>

      {/* Help Section */}
      <div className="text-center">
        <p className="text-sm text-gray-600 mb-2">Having trouble?</p>
        <div className="text-sm text-gray-500 space-y-1">
          <p>• Make sure your device's time is correct</p>
          <p>• Try refreshing the code in your authenticator app</p>
          <p>• Double-check you added the correct account</p>
        </div>
      </div>
    </div>
  );
};

export default TOTPVerificationStep;