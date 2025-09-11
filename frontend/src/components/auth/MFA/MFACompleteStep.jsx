'use client';

import React from 'react';
import { CheckCircle, Shield, Key, Download } from 'lucide-react';
import { Button } from '@/components/ui/Button';

const MFACompleteStep = ({ onComplete }) => {
  return (
    <div className="space-y-6 text-center">
      {/* Success Icon */}
      <div className="flex justify-center mb-6">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
          <CheckCircle className="h-12 w-12 text-green-600" />
        </div>
      </div>

      {/* Main Message */}
      <div className="space-y-4">
        <h3 className="text-2xl font-bold text-gray-900">
          Two-Factor Authentication Enabled!
        </h3>
        <p className="text-gray-600 text-lg">
          Your account is now protected with an additional layer of security.
        </p>
      </div>

      {/* Security Features Summary */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-left">
        <h4 className="font-semibold text-green-900 mb-4 flex items-center">
          <Shield className="h-5 w-5 mr-2" />
          What's Now Protected
        </h4>
        <div className="space-y-3 text-sm text-green-800">
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-green-600 rounded-full mt-2 flex-shrink-0"></div>
            <span>Your account login requires both your password and authenticator code</span>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-green-600 rounded-full mt-2 flex-shrink-0"></div>
            <span>You have backup codes saved for emergency access</span>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-green-600 rounded-full mt-2 flex-shrink-0"></div>
            <span>Unauthorized access is now significantly more difficult</span>
          </div>
        </div>
      </div>

      {/* Important Reminders */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-left">
        <h4 className="font-semibold text-blue-900 mb-4 flex items-center">
          <Key className="h-5 w-5 mr-2" />
          Important Reminders
        </h4>
        <div className="space-y-3 text-sm text-blue-800">
          <div className="flex items-start space-x-3">
            <div className="font-semibold text-blue-900 mt-0.5">📱</div>
            <span>Keep your authenticator app accessible - you'll need it for future logins</span>
          </div>
          <div className="flex items-start space-x-3">
            <div className="font-semibold text-blue-900 mt-0.5">🔐</div>
            <span>Store your backup codes in a safe, secure location</span>
          </div>
          <div className="flex items-start space-x-3">
            <div className="font-semibold text-blue-900 mt-0.5">⚠️</div>
            <span>Each backup code can only be used once</span>
          </div>
          <div className="flex items-start space-x-3">
            <div className="font-semibold text-blue-900 mt-0.5">🔄</div>
            <span>You can manage MFA settings from your account profile</span>
          </div>
        </div>
      </div>

      {/* Next Steps */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h4 className="font-semibold text-gray-900 mb-4">What happens next?</h4>
        <div className="text-sm text-gray-700 space-y-2">
          <p>• The next time you log in, you'll be prompted for your authenticator code</p>
          <p>• You can view and manage your MFA settings in your account profile</p>
          <p>• If you lose access to your authenticator, use your backup codes</p>
        </div>
      </div>

      {/* Completion Button */}
      <div className="pt-6">
        <Button
          onClick={onComplete}
          className="px-8 py-3 text-lg"
          size="lg"
        >
          Continue to Dashboard
        </Button>
      </div>

      {/* Help Text */}
      <div className="text-center pt-4">
        <p className="text-xs text-gray-500">
          Need help? Visit our security documentation or contact support
        </p>
      </div>
    </div>
  );
};

export default MFACompleteStep;