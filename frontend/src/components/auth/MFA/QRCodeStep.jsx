'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { QrCode, Smartphone, Copy, Eye, EyeOff, Loader2, AlertCircle } from 'lucide-react';
import { 
  selectMFAQRCode, 
  selectMFASecret,
  setMFAEnrollmentData,
  selectMFAIsEnrolling,
  setMFAEnrolling
} from '@/store/slices/authSlice';
import { useEnrollMFAMutation } from '@/store/api/authApi';
import { Button } from '@/components/ui/button';
import toast from 'react-hot-toast';

const QRCodeStep = ({ onNext }) => {
  const dispatch = useDispatch();
  const qrCode = useSelector(selectMFAQRCode);
  const secret = useSelector(selectMFASecret);
  const isEnrolling = useSelector(selectMFAIsEnrolling);
  const [showSecret, setShowSecret] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  const [enrollMFA, { isLoading: isEnrollingMFA }] = useEnrollMFAMutation();

  const startEnrollment = useCallback(async () => {
    if (!qrCode && !secret) {
      setIsLoading(true);
      try {
        const result = await enrollMFA().unwrap();
        dispatch(setMFAEnrollmentData(result));
        // Reset the enrolling state after successful QR code generation
        dispatch(setMFAEnrolling(false));
      } catch (error) {
        console.error('MFA enrollment initiation failed:', error);
        toast.error('Failed to start MFA setup. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }
  }, [enrollMFA, dispatch, qrCode, secret]);

  useEffect(() => {
    startEnrollment();
  }, [startEnrollment]);

  const copySecret = async () => {
    if (secret) {
      try {
        // Check if clipboard API is available (requires HTTPS or localhost)
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(secret);
          toast.success('Secret copied to clipboard!');
        } else {
          // Fallback for non-secure contexts
          const textArea = document.createElement('textarea');
          textArea.value = secret;
          textArea.style.position = 'absolute';
          textArea.style.left = '-999999px';
          textArea.style.top = '-999999px';
          document.body.appendChild(textArea);
          textArea.focus();
          textArea.select();
          
          try {
            const successful = document.execCommand('copy');
            if (successful) {
              toast.success('Secret copied to clipboard!');
            } else {
              throw new Error('Copy command failed');
            }
          } catch (err) {
            // If all else fails, show the secret and ask user to copy manually
            toast.error('Unable to copy automatically. Please copy the secret manually.');
            setShowSecret(true);
          } finally {
            document.body.removeChild(textArea);
          }
        }
      } catch (error) {
        console.error('Failed to copy secret:', error);
        toast.error('Unable to copy automatically. Please copy the secret manually.');
        setShowSecret(true);
      }
    }
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
        <div className="space-y-8 lg:space-y-0 lg:grid lg:grid-cols-2 lg:gap-8">
          {/* QR Code Section */}
          <div className="order-2 lg:order-1">
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-100 rounded-xl p-6 text-center">
              <h4 className="font-semibold text-gray-900 mb-6 flex items-center justify-center text-lg">
                <QrCode className="h-6 w-6 mr-2 text-blue-600" />
                Scan QR Code
              </h4>
              
              <div className="flex justify-center mb-6">
                <div className="bg-white p-6 rounded-2xl shadow-lg border-4 border-white">
                  <img 
                    src={qrCode} 
                    alt="MFA Setup QR Code" 
                    className="w-48 h-48 block mx-auto"
                    style={{ imageRendering: 'pixelated' }}
                  />
                </div>
              </div>
              
              <div className="space-y-3 text-sm text-gray-700">
                <p className="font-medium">📱 Open your authenticator app and scan this code</p>
                <div className="bg-white/70 rounded-lg p-3">
                  <p className="text-xs text-gray-600">
                    The QR code contains your secret key and account information for secure setup
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Manual Entry Section */}
          <div className="order-1 lg:order-2">
            <div className="bg-gradient-to-br from-gray-50 to-slate-50 border-2 border-gray-200 rounded-xl p-6">
              <h4 className="font-semibold text-gray-900 mb-6 flex items-center text-lg">
                <Smartphone className="h-6 w-6 mr-2 text-gray-600" />
                Manual Entry
              </h4>
              
              <p className="text-sm text-gray-600 mb-6">
                Can't scan the QR code? Enter this secret key manually in your authenticator app:
              </p>
              
              <div className="bg-white border-2 border-gray-200 rounded-xl p-4 mb-6">
                <div className="flex items-center justify-between">
                  <code className="text-sm sm:text-base font-mono text-gray-800 flex-1 mr-3 break-all">
                    {showSecret ? secret : '••••••••••••••••••••••••••••••••'}
                  </code>
                  <div className="flex items-center space-x-2 flex-shrink-0">
                    <button
                      onClick={() => setShowSecret(!showSecret)}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                      title={showSecret ? 'Hide secret' : 'Show secret'}
                    >
                      {showSecret ? (
                        <EyeOff className="h-5 w-5 text-gray-500" />
                      ) : (
                        <Eye className="h-5 w-5 text-gray-500" />
                      )}
                    </button>
                    <button
                      onClick={copySecret}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                      title="Copy secret"
                    >
                      <Copy className="h-5 w-5 text-gray-500" />
                    </button>
                  </div>
                </div>
              </div>

              <div className="bg-white/70 rounded-xl p-4">
                <h5 className="font-medium text-gray-900 mb-3">📝 Manual Setup Steps:</h5>
                <div className="space-y-3 text-sm text-gray-700">
                  <div className="flex items-start space-x-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-bold">1</span>
                    <span>Open your authenticator app</span>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-bold">2</span>
                    <span>Select "Add account manually" or "Enter setup key"</span>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-bold">3</span>
                    <span>Enter the secret key shown above</span>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-bold">4</span>
                    <span>Name the account "Gradvy" or "Gradvy Account"</span>
                  </div>
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
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-100 rounded-xl p-6">
        <h5 className="font-semibold text-gray-900 mb-4 text-center">🔐 Recommended Authenticator Apps</h5>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white/70 rounded-lg p-3 text-center hover:bg-white/90 transition-colors">
            <div className="text-2xl mb-1">📱</div>
            <div className="font-medium text-gray-900 text-sm">Google Authenticator</div>
            <div className="text-xs text-gray-600">Free • iOS & Android</div>
          </div>
          <div className="bg-white/70 rounded-lg p-3 text-center hover:bg-white/90 transition-colors">
            <div className="text-2xl mb-1">🛡️</div>
            <div className="font-medium text-gray-900 text-sm">Authy</div>
            <div className="text-xs text-gray-600">Multi-device • Cloud backup</div>
          </div>
          <div className="bg-white/70 rounded-lg p-3 text-center hover:bg-white/90 transition-colors">
            <div className="text-2xl mb-1">🪟</div>
            <div className="font-medium text-gray-900 text-sm">Microsoft Authenticator</div>
            <div className="text-xs text-gray-600">Enterprise features</div>
          </div>
        </div>
        <div className="text-center mt-4">
          <p className="text-xs text-gray-600">Any TOTP-compatible authenticator app will work with Gradvy</p>
        </div>
      </div>

    </div>
  );
};

export default QRCodeStep;