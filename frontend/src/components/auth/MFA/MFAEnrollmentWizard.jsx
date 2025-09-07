'use client';

import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ArrowLeft, ArrowRight, CheckCircle } from 'lucide-react';
import { 
  selectMFACurrentStep, 
  selectMFAIsEnrolling,
  setMFACurrentStep,
  setMFAEnrolling,
  clearMFAData 
} from '../../../store/slices/authSlice';
import { Button } from '../../ui/Button';
import { Card } from '../../ui/Card';
import QRCodeStep from './QRCodeStep';
import TOTPVerificationStep from './TOTPVerificationStep';
import BackupCodesStep from './BackupCodesStep';
import MFACompleteStep from './MFACompleteStep';
import toast from 'react-hot-toast';

const MFAEnrollmentWizard = ({ isOpen, onClose, onComplete }) => {
  const dispatch = useDispatch();
  const currentStep = useSelector(selectMFACurrentStep);
  const isEnrolling = useSelector(selectMFAIsEnrolling);

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

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return <QRCodeStep onNext={handleNext} />;
      case 1:
        return <TOTPVerificationStep onNext={handleNext} onPrevious={handlePrevious} />;
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-2xl"
      >
        <Card className="p-6 shadow-2xl">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Enable Two-Factor Authentication</h2>
              <p className="text-gray-600 mt-1">Secure your account with an additional layer of protection</p>
            </div>
            <button
              onClick={handleClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="h-5 w-5 text-gray-500" />
            </button>
          </div>

          {/* Progress Steps */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              {steps.map((step, index) => (
                <div key={step.id} className="flex items-center">
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                    ${currentStep >= step.id 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-200 text-gray-600'
                    }
                    ${currentStep === step.id ? 'ring-2 ring-blue-200' : ''}
                  `}>
                    {currentStep > step.id ? (
                      <CheckCircle className="h-4 w-4" />
                    ) : (
                      step.id + 1
                    )}
                  </div>
                  
                  {index < steps.length - 1 && (
                    <div className={`
                      w-12 sm:w-16 h-0.5 mx-2
                      ${currentStep > step.id ? 'bg-blue-600' : 'bg-gray-200'}
                    `} />
                  )}
                </div>
              ))}
            </div>
            
            <div className="text-center">
              <h3 className="font-semibold text-gray-900">{steps[currentStep]?.title}</h3>
              <p className="text-sm text-gray-600">{steps[currentStep]?.description}</p>
            </div>
          </div>

          {/* Step Content */}
          <div className="min-h-[400px]">
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

          {/* Navigation Buttons (only show for steps 0-2, step 3 handles its own) */}
          {currentStep < 3 && (
            <div className="flex justify-between mt-6 pt-4 border-t">
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
                disabled={isEnrolling}
                className="flex items-center"
              >
                {currentStep === 2 ? 'Finish Setup' : 'Continue'}
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          )}
        </Card>
      </motion.div>
    </div>
  );
};

export default MFAEnrollmentWizard;