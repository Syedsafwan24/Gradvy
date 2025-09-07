'use client';

import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { Key, Download, Copy, Eye, EyeOff, AlertTriangle } from 'lucide-react';
import { selectMFABackupCodes } from '../../../store/slices/authSlice';
import { Button } from '../../ui/Button';
import toast from 'react-hot-toast';

const BackupCodesStep = ({ onNext, onPrevious }) => {
  const backupCodes = useSelector(selectMFABackupCodes);
  const [showCodes, setShowCodes] = useState(true);
  const [acknowledged, setAcknowledged] = useState(false);

  // If no backup codes in state, use mock data for demo
  const codes = backupCodes?.length ? backupCodes : [
    'ABC123DEF',
    'GHI456JKL',
    'MNO789PQR',
    'STU012VWX',
    'YZ3456ABC',
    'DEF789GHI',
    'JKL012MNO',
    'PQR345STU'
  ];

  const copyAllCodes = async () => {
    try {
      const codesText = codes.map((code, index) => `${index + 1}. ${code}`).join('\n');
      await navigator.clipboard.writeText(codesText);
      toast.success('All backup codes copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy codes:', error);
      toast.error('Failed to copy codes');
    }
  };

  const downloadCodes = () => {
    const codesText = [
      'Gradvy Account - MFA Backup Codes',
      '===============================',
      'Generated: ' + new Date().toLocaleDateString(),
      '',
      'IMPORTANT: Keep these codes safe and secure!',
      'Each code can only be used once.',
      '',
      ...codes.map((code, index) => `${index + 1}. ${code}`),
      '',
      '⚠️  Store these codes in a safe place:',
      '   • Save them in a password manager',
      '   • Print them and store securely',
      '   • Do NOT store them in plain text files',
      '   • Do NOT share them with anyone',
    ].join('\n');

    const blob = new Blob([codesText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `gradvy-backup-codes-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success('Backup codes downloaded!');
  };

  const handleContinue = () => {
    if (!acknowledged) {
      toast.error('Please acknowledge that you have saved your backup codes.');
      return;
    }
    onNext();
  };

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Key className="h-8 w-8 text-yellow-600" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Save Your Backup Codes</h3>
        <p className="text-gray-600">
          These backup codes can be used to access your account if you lose your authenticator device.
        </p>
      </div>

      {/* Warning Alert */}
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm">
            <h4 className="font-semibold text-red-800 mb-1">Important Security Notice</h4>
            <ul className="text-red-700 space-y-1">
              <li>• Each code can only be used once</li>
              <li>• Store these codes in a safe, secure location</li>
              <li>• Do not share these codes with anyone</li>
              <li>• If you lose these codes, you may lose access to your account</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Backup Codes */}
      <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="font-semibold text-gray-900">Your Backup Codes</h4>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowCodes(!showCodes)}
              className="p-2 hover:bg-gray-200 rounded transition-colors"
              title={showCodes ? 'Hide codes' : 'Show codes'}
            >
              {showCodes ? (
                <EyeOff className="h-4 w-4 text-gray-600" />
              ) : (
                <Eye className="h-4 w-4 text-gray-600" />
              )}
            </button>
            <button
              onClick={copyAllCodes}
              className="p-2 hover:bg-gray-200 rounded transition-colors"
              title="Copy all codes"
            >
              <Copy className="h-4 w-4 text-gray-600" />
            </button>
            <button
              onClick={downloadCodes}
              className="p-2 hover:bg-gray-200 rounded transition-colors"
              title="Download codes"
            >
              <Download className="h-4 w-4 text-gray-600" />
            </button>
          </div>
        </div>

        {showCodes ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {codes.map((code, index) => (
              <div
                key={index}
                className="bg-white border rounded p-3 font-mono text-center text-lg font-semibold text-gray-800"
              >
                {index + 1}. {code}
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white border rounded p-8 text-center">
            <div className="text-gray-400 space-y-2">
              <Eye className="h-8 w-8 mx-auto" />
              <p>Backup codes are hidden</p>
              <p className="text-sm">Click the eye icon to show them</p>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Button
          onClick={copyAllCodes}
          variant="outline"
          className="flex-1 flex items-center justify-center"
        >
          <Copy className="h-4 w-4 mr-2" />
          Copy All Codes
        </Button>
        <Button
          onClick={downloadCodes}
          variant="outline"
          className="flex-1 flex items-center justify-center"
        >
          <Download className="h-4 w-4 mr-2" />
          Download as File
        </Button>
      </div>

      {/* Storage Suggestions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h5 className="font-semibold text-blue-900 mb-2">Recommended Storage Options:</h5>
        <div className="text-sm text-blue-800 space-y-1">
          <div>🔐 <strong>Password Manager:</strong> Store in your password manager's secure notes</div>
          <div>📄 <strong>Physical Copy:</strong> Print and store in a safe place</div>
          <div>☁️ <strong>Encrypted Storage:</strong> Save in encrypted cloud storage</div>
          <div>🏦 <strong>Safe Deposit Box:</strong> For maximum security</div>
        </div>
      </div>

      {/* Acknowledgment Checkbox */}
      <div className="bg-white border-2 border-gray-300 rounded-lg p-4">
        <label className="flex items-start space-x-3 cursor-pointer">
          <input
            type="checkbox"
            checked={acknowledged}
            onChange={(e) => setAcknowledged(e.target.checked)}
            className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <div className="text-sm">
            <div className="font-medium text-gray-900">
              I have saved my backup codes in a secure location
            </div>
            <div className="text-gray-600 mt-1">
              I understand that these codes are required to access my account if I lose my authenticator device, 
              and that each code can only be used once.
            </div>
          </div>
        </label>
      </div>

      {/* Continue Button */}
      <div className="flex justify-center pt-4">
        <Button
          onClick={handleContinue}
          disabled={!acknowledged}
          className="px-8"
        >
          I've Saved My Backup Codes
        </Button>
      </div>
    </div>
  );
};

export default BackupCodesStep;