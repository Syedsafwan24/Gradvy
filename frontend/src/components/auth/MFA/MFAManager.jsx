'use client';

import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Shield, Settings, Eye, EyeOff, Download, RefreshCw, XCircle, Plus } from 'lucide-react';
import { 
  selectCurrentUser,
  selectMFABackupCodes,
  setMFABackupCodes 
} from '@/store/slices/authSlice';
import { 
  useDisableMFAMutation,
  useGetMFAStatusQuery,
  useGetMFABackupCodesQuery 
} from '@/store/api/authApi';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import MFAEnrollmentWizard from './MFAEnrollmentWizard';
import BackupCodesManager from './BackupCodesManager';
import toast from 'react-hot-toast';

const MFAManager = ({ compact = false }) => {
  const dispatch = useDispatch();
  const user = useSelector(selectCurrentUser);
  const backupCodes = useSelector(selectMFABackupCodes);
  
  const [showEnrollmentWizard, setShowEnrollmentWizard] = useState(false);
  const [showBackupManager, setShowBackupManager] = useState(false);
  
  // API hooks
  const [disableMFA, { isLoading: isDisablingMFA }] = useDisableMFAMutation();
  const { data: mfaStatus, isLoading: isLoadingStatus, refetch: refetchStatus } = useGetMFAStatusQuery();
  const { data: backupCodesData, isLoading: isLoadingCodes } = useGetMFABackupCodesQuery(
    undefined, 
    { skip: !user?.is_mfa_enabled }
  );

  const handleEnableMFA = () => {
    setShowEnrollmentWizard(true);
  };

  const handleDisableMFA = async () => {
    if (!window.confirm('Are you sure you want to disable two-factor authentication? This will make your account less secure.')) {
      return;
    }

    try {
      await disableMFA().unwrap();
      dispatch(setMFABackupCodes([])); // Clear backup codes from state
      toast.success('Two-factor authentication disabled');
    } catch (error) {
      console.error('MFA disable failed:', error);
      toast.error('Failed to disable MFA. Please try again.');
    }
  };

  const handleEnrollmentComplete = () => {
    setShowEnrollmentWizard(false);
    refetchStatus(); // Refresh MFA status after enrollment
    toast.success('Two-factor authentication enabled successfully!');
  };

  // Use real API data or fallback to user data
  const isMFAEnabled = mfaStatus?.is_mfa_enabled ?? user?.is_mfa_enabled ?? false;
  const hasBackupCodes = backupCodesData?.backup_codes?.length > 0;

  if (compact) {
    return (
      <div className="space-y-4">
        {/* Loading state */}
        {isLoadingStatus && (
          <div className="flex items-center justify-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2 text-sm text-gray-600">Loading MFA status...</span>
          </div>
        )}

        {!isLoadingStatus && (
          <>
            {/* Compact MFA Status */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Shield className={`h-5 w-5 ${isMFAEnabled ? 'text-green-600' : 'text-gray-400'}`} />
                <div>
                  <span className="text-sm font-medium text-gray-900">Two-Factor Authentication</span>
                  <p className="text-xs text-gray-600">
                    {isMFAEnabled ? 'Active and protecting your account' : 'Not enabled'}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  isMFAEnabled 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {isMFAEnabled ? 'Enabled' : 'Disabled'}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={isMFAEnabled ? () => setShowBackupManager(true) : handleEnableMFA}
                  disabled={isDisablingMFA}
                >
                  <Settings className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </>
        )}

        {/* MFA Wizards and Managers */}
        <MFAEnrollmentWizard
          isOpen={showEnrollmentWizard}
          onClose={() => setShowEnrollmentWizard(false)}
          onComplete={handleEnrollmentComplete}
        />

        <BackupCodesManager
          isOpen={showBackupManager}
          onClose={() => setShowBackupManager(false)}
          onDisableMFA={handleDisableMFA}
          isDisablingMFA={isDisablingMFA}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Loading state for full component */}
      {isLoadingStatus && (
        <div className="flex flex-col items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Loading MFA Settings</h3>
          <p className="text-gray-600 text-center">Please wait while we fetch your security settings...</p>
        </div>
      )}

      {!isLoadingStatus && isMFAEnabled ? (
        /* MFA Enabled State */
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-start space-x-3">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Shield className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Two-Factor Authentication Active</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Your account is protected with an additional layer of security
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-1 bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
              <Shield className="h-4 w-4" />
              <span>Protected</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button
              variant="outline"
              onClick={() => setShowBackupManager(true)}
              className="flex items-center justify-center"
            >
              <Eye className="h-4 w-4 mr-2" />
              Manage Backup Codes
            </Button>
            
            <Button
              variant="destructive"
              onClick={handleDisableMFA}
              disabled={isDisablingMFA}
              className="flex items-center justify-center"
            >
              <XCircle className="h-4 w-4 mr-2" />
              {isDisablingMFA ? 'Disabling...' : 'Disable 2FA'}
            </Button>
          </div>
        </Card>
      ) : !isLoadingStatus ? (
        /* MFA Disabled State */
        <Card className="p-6">
          <div className="flex items-start space-x-3 mb-6">
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Shield className="h-6 w-6 text-yellow-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Secure Your Account</h3>
              <p className="text-sm text-gray-600 mt-1">
                Two-factor authentication adds an extra layer of security to your account
              </p>
            </div>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <h4 className="font-semibold text-yellow-900 mb-2">Why enable 2FA?</h4>
            <ul className="text-sm text-yellow-800 space-y-1">
              <li>• Protects against password-only attacks</li>
              <li>• Adds security even if your password is compromised</li>
              <li>• Required for accessing sensitive features</li>
              <li>• Industry standard security practice</li>
            </ul>
          </div>

          <Button
            onClick={handleEnableMFA}
            className="w-full sm:w-auto flex items-center justify-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            Enable Two-Factor Authentication
          </Button>
        </Card>
      ) : null}

      {/* MFA Wizards and Managers */}
      <MFAEnrollmentWizard
        isOpen={showEnrollmentWizard}
        onClose={() => setShowEnrollmentWizard(false)}
        onComplete={handleEnrollmentComplete}
      />

      <BackupCodesManager
        isOpen={showBackupManager}
        onClose={() => setShowBackupManager(false)}
        onDisableMFA={handleDisableMFA}
        isDisablingMFA={isDisablingMFA}
      />
    </div>
  );
};

export default MFAManager;