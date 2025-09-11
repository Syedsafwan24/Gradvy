'use client';

import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ArrowLeft, ArrowRight, CheckCircle } from 'lucide-react';
import { 
  selectMFACurrentStep, 
  selectMFAIsEnrolling,
  selectMFAQRCode,
  selectMFASecret,
  setMFACurrentStep,
  setMFAEnrolling,
  clearMFAData 
} from '@/store/slices/authSlice';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import QRCodeStep from './QRCodeStep';
import TOTPVerificationStep from './TOTPVerificationStep';
import BackupCodesStep from './BackupCodesStep';
import MFACompleteStep from './MFACompleteStep';
import toast from 'react-hot-toast';

const MFAEnrollmentWizard = ({ isOpen, onClose, onComplete }) => {
  const dispatch = useDispatch();
  const currentStep = useSelector(selectMFACurrentStep);
  const isEnrolling = useSelector(selectMFAIsEnrolling);
  const qrCode = useSelector(selectMFAQRCode);
  const secret = useSelector(selectMFASecret);
  const [stepCompletionState, setStepCompletionState] = useState({});

  const steps = [
    { id: 0, title: 'Setup Authenticator', description: 'Scan QR code with your authenticator app' },
    { id: 1, title: 'Verify Code', description: 'Enter code from your authenticator app' },
    { id: 2, title: 'Backup Codes', description: 'Save your backup codes safely' },
    { id: 3, title: 'Complete', description: 'MFA setup complete!' }
  ];

  useEffect(() => {
    if (isOpen) {
      dispatch(setMFACurrentStep(0));
      dispatch(setMFAEnrolling(true));
    }
  }, [isOpen, dispatch]);

  const handleClose = () => {
    dispatch(clearMFAData());
    dispatch(setMFAEnrolling(false));
    onClose();
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      dispatch(setMFACurrentStep(currentStep + 1));
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      dispatch(setMFACurrentStep(currentStep - 1));
    }
  };

  const handleComplete = () => {
    dispatch(clearMFAData());
    dispatch(setMFAEnrolling(false));
    onComplete?.();
    onClose();
    toast.success('MFA enabled successfully!');
  };

  const isStepComplete = () => {
    // Step 0 (QR): Always allow continue after QR is loaded
    if (currentStep === 0) return true;
    // Step 1 (TOTP): Check if verification is complete
    if (currentStep === 1) return stepCompletionState[1] === true;
    // Step 2 (Backup): Always allow continue
    if (currentStep === 2) return true;
    return false;
  };

  const markStepComplete = (step) => {
    setStepCompletionState(prev => ({ ...prev, [step]: true }));
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return <QRCodeStep onNext={handleNext} />;
      case 1:
        return <TOTPVerificationStep onNext={handleNext} onPrevious={handlePrevious} onStepComplete={() => markStepComplete(1)} />;
      case 2:
        return <BackupCodesStep onNext={handleNext} onPrevious={handlePrevious} />;
      case 3:
        return <MFACompleteStep onComplete={handleComplete} />;
      default:
        return null;
    }
  };

  const stepVariants = {
    hidden: { opacity: 0, x: 50 },
    visible: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -50 }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-2 sm:p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="w-full max-w-4xl max-h-[95vh] sm:max-h-[90vh] flex flex-col rounded-lg bg-white shadow-2xl"
        >
            {/* Fixed Header */}
            <div className="flex-shrink-0 border-b border-gray-200 px-4 py-4 sm:px-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl sm:text-2xl font-bold text-gray-900">Enable Two-Factor Authentication</h2>
                  <p className="text-sm sm:text-base text-gray-600 mt-1">
                    Step {currentStep + 1} of {steps.length}: {steps[currentStep]?.title}
                  </p>
                </div>
                <button
                  onClick={handleClose}
                  className="flex-shrink-0 p-2 hover:bg-gray-100 rounded-full transition-colors"
                >
                  <X className="h-5 w-5 text-gray-500" />
                </button>
              </div>
              
              {/* Progress Steps in Header */}
              <div className="mt-4 px-2">
                <div className="flex items-center justify-between">
                  {steps.map((step, index) => (
                    <div key={step.id} className="flex items-center flex-1">
                      <div className={`
                        w-6 h-6 sm:w-8 sm:h-8 rounded-full flex items-center justify-center text-xs sm:text-sm font-medium
                        ${currentStep >= step.id 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-gray-200 text-gray-600'
                        }
                        ${currentStep === step.id ? 'ring-2 ring-blue-200' : ''}
                      `}>
                        {currentStep > step.id ? (
                          <CheckCircle className="h-3 w-3 sm:h-4 sm:w-4" />
                        ) : (
                          step.id + 1
                        )}
                      </div>
                      
                      {index < steps.length - 1 && (
                        <div className={`
                          flex-1 h-0.5 mx-2
                          ${currentStep > step.id ? 'bg-blue-600' : 'bg-gray-200'}
                        `} />
                      )}
                    </div>
                  ))}
                </div>
                
                <div className="text-center mt-3">
                  <p className="text-xs sm:text-sm text-gray-600">{steps[currentStep]?.description}</p>
                </div>
              </div>
            </div>

            {/* Scrollable Content Body */}
            <div className="flex-1 min-h-0 overflow-y-auto px-4 py-6 sm:px-6">
              <AnimatePresence mode="wait">
                <motion.div
                  key={currentStep}
                  variants={stepVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  {renderStepContent()}
                </motion.div>
              </AnimatePresence>
            </div>

            {/* Fixed Footer with Navigation */}
            {currentStep < 3 && (
              <div className="flex-shrink-0 border-t border-gray-200 px-4 py-4 sm:px-6">
                <div className="flex justify-between">
                  <Button
                    variant="outline"
                    onClick={currentStep === 0 ? handleClose : handlePrevious}
                    className="flex items-center"
                  >
                    {currentStep === 0 ? (
                      <>
                        <X className="h-4 w-4 mr-2" />
                        Cancel
                      </>
                    ) : (
                      <>
                        <ArrowLeft className="h-4 w-4 mr-2" />
                        Previous
                      </>
                    )}
                  </Button>

                  <Button
                    onClick={handleNext}
                    disabled={isEnrolling || (currentStep === 1 && !isStepComplete())}
                    className="flex items-center"
                  >
                    {currentStep === 2 ? 'Finish Setup' : 'Continue'}
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </div>
              </div>
            )}
        </motion.div>
      </div>
    </div>
  );
};

export default MFAEnrollmentWizard;