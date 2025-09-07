'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Shield, Loader2 } from 'lucide-react';
import { Button } from '../../ui/Button';
import toast from 'react-hot-toast';

// Validation schema
const verificationSchema = yup.object({
  code: yup
    .string()
    .matches(/^\d{6}$/, 'Code must be 6 digits')
    .required('Verification code is required'),
});

const TOTPVerificationStep = ({ onNext, onPrevious }) => {
  const [isVerifying, setIsVerifying] = useState(false);

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

  const onSubmit = async (data) => {
    setIsVerifying(true);
    
    try {
      // TODO: Implement actual TOTP verification with the backend
      // For now, simulate verification
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // In a real implementation, you would call an API like:
      // await verifyMFASetup({ code: data.code }).unwrap();
      
      toast.success('Code verified successfully!');
      onNext();
    } catch (error) {
      console.error('TOTP verification failed:', error);
      toast.error('Invalid code. Please try again.');
    } finally {
      setIsVerifying(false);
    }
  };

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

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
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
              value={codeValue}
              className={`
                w-48 px-4 py-3 text-center text-2xl font-mono tracking-widest
                border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                transition-colors ${errors.code ? 'border-red-500' : 'border-gray-300'}
              `}
              disabled={isVerifying}
            />
          </div>
          {errors.code && (
            <p className="mt-2 text-sm text-red-600 text-center">{errors.code.message}</p>
          )}
        </div>

        {/* Visual Code Input */}
        <div className="flex justify-center space-x-2">
          {Array.from({ length: 6 }).map((_, index) => (
            <div
              key={index}
              className={`
                w-10 h-12 border-2 rounded-lg flex items-center justify-center
                text-xl font-mono font-semibold
                ${index < codeValue.length 
                  ? 'border-blue-500 bg-blue-50 text-blue-900' 
                  : 'border-gray-300 bg-gray-50 text-gray-400'
                }
              `}
            >
              {codeValue[index] || ''}
            </div>
          ))}
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 className="font-semibold text-yellow-800 mb-2">Tips for getting your code:</h4>
          <ul className="text-sm text-yellow-700 space-y-1">
            <li>• Open your authenticator app</li>
            <li>• Find the "Gradvy" or similar account you just added</li>
            <li>• Enter the current 6-digit code (it updates every 30 seconds)</li>
            <li>• Make sure to enter the code before it expires</li>
          </ul>
        </div>

        {/* Submit Button */}
        <div className="flex justify-center">
          <Button
            type="submit"
            disabled={isVerifying || codeValue.length !== 6}
            className="px-8"
          >
            {isVerifying ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Verifying...
              </>
            ) : (
              'Verify & Continue'
            )}
          </Button>
        </div>
      </form>

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