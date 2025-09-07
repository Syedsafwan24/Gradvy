'use client';

import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { 
  X, 
  Eye, 
  EyeOff, 
  Download, 
  Copy, 
  RefreshCw, 
  AlertTriangle, 
  Shield,
  Key,
  XCircle
} from 'lucide-react';
import { 
  selectMFABackupCodes,
  setMFABackupCodes 
} from '../../../store/slices/authSlice';
import { Button } from '../../ui/Button';
import { Card } from '../../ui/Card';
import toast from 'react-hot-toast';

const BackupCodesManager = ({ 
  isOpen, 
  onClose, 
  onDisableMFA, 
  isDisablingMFA = false 
}) => {
  const dispatch = useDispatch();
  const backupCodes = useSelector(selectMFABackupCodes);
  const [showCodes, setShowCodes] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [acknowledgedSaved, setAcknowledgedSaved] = useState(false);

  // Mock backup codes if none exist in state (for demo purposes)
  const codes = backupCodes?.length ? backupCodes : [
    'ABC123DEF456',
    'GHI789JKL012', 
    'MNO345PQR678',
    'STU901VWX234',
    'YZ5678ABC901',
    'DEF234GHI567',
    'JKL890MNO123',
    'PQR456STU789'
  ];

  useEffect(() => {
    if (isOpen) {
      setShowCodes(false);
      setAcknowledgedSaved(false);
    }
  }, [isOpen]);

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

  const regenerateBackupCodes = async () => {
    if (!window.confirm('Are you sure you want to generate new backup codes? Your old backup codes will no longer work.')) {
      return;
    }

    setIsRegenerating(true);
    
    try {
      // TODO: Implement actual API call to regenerate backup codes
      // For now, simulate the API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Generate new mock codes
      const newCodes = [
        'NEW123ABC456',
        'DEF789GHI012',
        'JKL345MNO678', 
        'PQR901STU234',
        'VWX567YZ8901',
        'ABC234DEF567',
        'GHI890JKL123',
        'MNO456PQR789'
      ];
      
      dispatch(setMFABackupCodes(newCodes));
      setShowCodes(true);
      setAcknowledgedSaved(false);
      toast.success('New backup codes generated!');
    } catch (error) {
      console.error('Failed to regenerate backup codes:', error);
      toast.error('Failed to regenerate backup codes');
    } finally {
      setIsRegenerating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="w-full max-w-2xl max-h-screen overflow-y-auto">
        <Card className="p-6 shadow-2xl">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                <Key className="h-6 w-6 mr-2" />
                Backup Codes Management
              </h2>
              <p className="text-gray-600 mt-1">View, download, or regenerate your MFA backup codes</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="h-5 w-5 text-gray-500" />
            </button>
          </div>

          {/* Security Warning */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm">
                <h4 className="font-semibold text-red-800 mb-1">Important Security Information</h4>
                <ul className="text-red-700 space-y-1">
                  <li>• Each backup code can only be used once</li>
                  <li>• Store these codes in a safe, secure location</li>
                  <li>• Do not share these codes with anyone</li>
                  <li>• If you lose these codes, you may lose access to your account</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Backup Codes Display */}
          <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6 mb-6">
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
          <div className="flex flex-col sm:flex-row gap-3 mb-6">
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
            <Button
              onClick={regenerateBackupCodes}
              variant="outline"
              disabled={isRegenerating}
              className="flex-1 flex items-center justify-center"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRegenerating ? 'animate-spin' : ''}`} />
              {isRegenerating ? 'Generating...' : 'Generate New'}
            </Button>
          </div>

          {/* Storage Recommendations */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h5 className="font-semibold text-blue-900 mb-2">Recommended Storage Options:</h5>
            <div className="text-sm text-blue-800 space-y-1">
              <div>🔐 <strong>Password Manager:</strong> Store in your password manager's secure notes</div>
              <div>📄 <strong>Physical Copy:</strong> Print and store in a safe place</div>
              <div>☁️ <strong>Encrypted Storage:</strong> Save in encrypted cloud storage</div>
              <div>🏦 <strong>Safe Deposit Box:</strong> For maximum security</div>
            </div>
          </div>

          {/* Acknowledgment and Actions */}
          <div className="space-y-4">
            <div className="bg-white border-2 border-gray-300 rounded-lg p-4">
              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={acknowledgedSaved}
                  onChange={(e) => setAcknowledgedSaved(e.target.checked)}
                  className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div className="text-sm">
                  <div className="font-medium text-gray-900">
                    I have saved my backup codes in a secure location
                  </div>
                  <div className="text-gray-600 mt-1">
                    I understand that these codes are required to access my account if I lose my authenticator device.
                  </div>
                </div>
              </label>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <Button
                onClick={onClose}
                disabled={!acknowledgedSaved}
                className="flex-1"
              >
                Done
              </Button>
              <Button
                variant="destructive"
                onClick={onDisableMFA}
                disabled={isDisablingMFA}
                className="flex-1"
              >
                <XCircle className="h-4 w-4 mr-2" />
                {isDisablingMFA ? 'Disabling 2FA...' : 'Disable 2FA'}
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default BackupCodesManager;