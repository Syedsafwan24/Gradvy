'use client';

import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { QrCode, Smartphone, Copy, Eye, EyeOff, Loader2, AlertCircle } from 'lucide-react';
import { 
  selectMFAQRCode, 
  selectMFASecret,
  setMFAEnrollmentData,
  selectMFAIsEnrolling 
} from '../../../store/slices/authSlice';
import { useEnrollMFAMutation } from '../../../store/api/authApi';
import { Button } from '../../ui/Button';
import toast from 'react-hot-toast';

const QRCodeStep = ({ onNext }) => {
  const dispatch = useDispatch();
  const qrCode = useSelector(selectMFAQRCode);
  const secret = useSelector(selectMFASecret);
  const isEnrolling = useSelector(selectMFAIsEnrolling);
  const [showSecret, setShowSecret] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  const [enrollMFA, { isLoading: isEnrollingMFA }] = useEnrollMFAMutation();

  useEffect(() => {
    // Start MFA enrollment when component mounts
    const startEnrollment = async () => {
      if (!qrCode && !secret) {
        setIsLoading(true);
        try {
          const result = await enrollMFA().unwrap();
          dispatch(setMFAEnrollmentData(result));
        } catch (error) {
          console.error('MFA enrollment initiation failed:', error);
          toast.error('Failed to start MFA setup. Please try again.');
        } finally {
          setIsLoading(false);
        }
      }
    };

    startEnrollment();
  }, [enrollMFA, dispatch, qrCode, secret]);

  const copySecret = async () => {
    if (secret) {
      try {
        await navigator.clipboard.writeText(secret);
        toast.success('Secret copied to clipboard!');
      } catch (error) {
        console.error('Failed to copy secret:', error);
        toast.error('Failed to copy secret');
      }
    }
  };

  const handleContinue = () => {
    if (!secret) {
      toast.error('MFA setup not ready. Please wait or try again.');
      return;
    }
    onNext();
  };

  if (isLoading || isEnrollingMFA) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600 mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Setting up MFA</h3>
        <p className="text-gray-600 text-center">Please wait while we generate your authentication codes...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <QrCode className="h-8 w-8 text-blue-600" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Setup Your Authenticator App</h3>
        <p className="text-gray-600">
          Scan the QR code below with your authenticator app or enter the secret key manually.
        </p>
      </div>

      {qrCode ? (
        <div className="flex flex-col lg:flex-row gap-8">
          {/* QR Code Section */}
          <div className="flex-1">
            <div className="bg-white border-2 border-gray-200 rounded-lg p-6 text-center">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center justify-center">
                <QrCode className="h-5 w-5 mr-2" />
                Scan QR Code
              </h4>
              
              <div className="bg-white p-4 rounded-lg border inline-block">
                <img 
                  src={qrCode} 
                  alt="MFA QR Code" 
                  className="w-48 h-48 mx-auto"
                />
              </div>
              
              <p className="text-sm text-gray-600 mt-4">
                Scan this QR code with any authenticator app like Google Authenticator, 
                Authy, or Microsoft Authenticator.
              </p>
            </div>
          </div>

          {/* Manual Entry Section */}
          <div className="flex-1">
            <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <Smartphone className="h-5 w-5 mr-2" />
                Manual Entry
              </h4>
              
              <p className="text-sm text-gray-600 mb-4">
                If you can't scan the QR code, you can enter this secret key manually:
              </p>
              
              <div className="bg-white border rounded-lg p-3 mb-4">
                <div className="flex items-center justify-between">
                  <code className="text-sm font-mono text-gray-800 flex-1 mr-2">
                    {showSecret ? secret : '••••••••••••••••••••••••••••••••'}
                  </code>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setShowSecret(!showSecret)}
                      className="p-1 hover:bg-gray-100 rounded transition-colors"
                      title={showSecret ? 'Hide secret' : 'Show secret'}
                    >
                      {showSecret ? (
                        <EyeOff className="h-4 w-4 text-gray-500" />
                      ) : (
                        <Eye className="h-4 w-4 text-gray-500" />
                      )}
                    </button>
                    <button
                      onClick={copySecret}
                      className="p-1 hover:bg-gray-100 rounded transition-colors"
                      title="Copy secret"
                    >
                      <Copy className="h-4 w-4 text-gray-500" />
                    </button>
                  </div>
                </div>
              </div>

              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-start space-x-2">
                  <span className="font-semibold text-gray-700 mt-0.5">1.</span>
                  <span>Open your authenticator app</span>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="font-semibold text-gray-700 mt-0.5">2.</span>
                  <span>Add a new account manually</span>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="font-semibold text-gray-700 mt-0.5">3.</span>
                  <span>Enter the secret key above</span>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="font-semibold text-gray-700 mt-0.5">4.</span>
                  <span>Name it "Gradvy" or similar</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-8">
          <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Setup Failed</h3>
          <p className="text-gray-600 text-center mb-4">
            We couldn't generate your MFA setup codes. Please try again.
          </p>
          <Button 
            onClick={() => window.location.reload()} 
            variant="outline"
          >
            Try Again
          </Button>
        </div>
      )}

      {/* Popular Authenticator Apps */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h5 className="font-semibold text-blue-900 mb-2">Recommended Authenticator Apps:</h5>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-sm">
          <div className="text-blue-800">📱 Google Authenticator</div>
          <div className="text-blue-800">🔐 Authy</div>
          <div className="text-blue-800">🪟 Microsoft Authenticator</div>
        </div>
      </div>

      {/* Continue Button */}
      <div className="flex justify-center pt-4">
        <Button
          onClick={handleContinue}
          disabled={!secret}
          className="px-8"
        >
          I've Added the Account
        </Button>
      </div>
    </div>
  );
};

export default QRCodeStep;