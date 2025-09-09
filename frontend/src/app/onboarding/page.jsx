'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSelector, useDispatch } from 'react-redux';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { ArrowLeft, ArrowRight, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { useSubmitOnboardingMutation, useSaveOnboardingProgressMutation, preferencesApi } from '@/services/preferencesApi';

// Import onboarding step components
import WelcomeStep from '@/components/onboarding/WelcomeStep';
import GoalsStep from '@/components/onboarding/GoalsStep';
import ExperienceStep from '@/components/onboarding/ExperienceStep';
import PreferencesStep from '@/components/onboarding/PreferencesStep';
import AvailabilityStep from '@/components/onboarding/AvailabilityStep';
import CompletionStep from '@/components/onboarding/CompletionStep';

const ONBOARDING_STEPS = [
  {
    id: 'welcome',
    title: 'Welcome to Gradvy',
    component: WelcomeStep,
    canSkip: false,
    isRequired: true,
    conditions: null
  },
  {
    id: 'goals',
    title: 'What do you want to learn?',
    component: GoalsStep,
    canSkip: false,
    isRequired: true,
    conditions: null,
    validation: (data) => data.learning_goals && data.learning_goals.length > 0
  },
  {
    id: 'experience',
    title: "What's your experience level?",
    component: ExperienceStep,
    canSkip: false,
    isRequired: true,
    conditions: null,
    validation: (data) => data.experience_level && data.experience_level.length > 0
  },
  {
    id: 'preferences',
    title: 'How do you prefer to learn?',
    component: PreferencesStep,
    canSkip: false,
    isRequired: true,
    conditions: null,
    validation: (data) => {
      return data.learning_style && data.learning_style.length > 0 &&
             data.preferred_pace && data.career_stage && data.target_timeline;
    }
  },
  {
    id: 'availability',
    title: 'Tell us about your schedule',
    component: AvailabilityStep,
    canSkip: false,
    isRequired: true,
    conditions: null,
    validation: (data) => {
      return data.time_availability && 
             data.preferred_platforms && data.preferred_platforms.length > 0 &&
             data.content_types && data.content_types.length > 0 &&
             data.language_preference && data.language_preference.length > 0;
    }
  },
  {
    id: 'completion',
    title: 'You\'re all set!',
    component: CompletionStep,
    canSkip: false,
    isRequired: true,
    conditions: null
  }
];

export default function OnboardingPage() {
  const router = useRouter();
  const dispatch = useDispatch();
  const { user, isAuthenticated } = useSelector(state => state.auth);
  
  // RTK Query mutations
  const [submitOnboarding, { isLoading: isSubmitting, error: submitError }] = useSubmitOnboardingMutation();
  const [saveProgress, { isLoading: isSaving }] = useSaveOnboardingProgressMutation();
  
  const [currentStep, setCurrentStep] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [completedSteps, setCompletedSteps] = useState(new Set([0])); // Welcome step is auto-completed
  const [stepErrors, setStepErrors] = useState({});
  const [formData, setFormData] = useState({
    // Step 2: Goals
    learning_goals: [],
    
    // Step 3: Experience
    experience_level: '',
    
    // Step 4: Preferences
    preferred_pace: '',
    learning_style: [],
    career_stage: '',
    target_timeline: '',
    
    // Step 5: Availability
    time_availability: '',
    preferred_platforms: [],
    content_types: [],
    language_preference: ['english']
  });

  // Redirect if not authenticated and track onboarding start
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login?redirect=/onboarding');
    } else {
      // Track onboarding start time
      setFormData(prev => ({
        ...prev,
        _startTime: Date.now()
      }));

      // Track page visit
      const trackStart = async () => {
        try {
          await fetch('/api/preferences/interactions/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            },
            body: JSON.stringify({
              type: 'onboarding_started',
              data: {
                start_time: new Date().toISOString(),
                user_agent: navigator.userAgent,
                screen_resolution: `${screen.width}x${screen.height}`,
              },
              context: {
                source: 'onboarding_page',
                referrer: document.referrer,
              }
            })
          });
        } catch (error) {
          console.warn('Failed to track onboarding start:', error);
        }
      };

      trackStart();
    }
  }, [isAuthenticated, router]);

  // Calculate progress percentage
  const progressPercentage = ((currentStep + 1) / ONBOARDING_STEPS.length) * 100;

  // Smart validation for current step
  const validateCurrentStep = () => {
    const currentStepData = ONBOARDING_STEPS[currentStep];
    if (currentStepData.validation) {
      return currentStepData.validation(formData);
    }
    return true;
  };

  // Check if step should be shown based on conditions
  const shouldShowStep = (stepIndex) => {
    const step = ONBOARDING_STEPS[stepIndex];
    if (!step.conditions) return true;
    
    return step.conditions(formData);
  };

  // Get next valid step index
  const getNextStepIndex = (fromIndex) => {
    for (let i = fromIndex + 1; i < ONBOARDING_STEPS.length; i++) {
      if (shouldShowStep(i)) {
        return i;
      }
    }
    return ONBOARDING_STEPS.length - 1;
  };

  // Save progress after each step
  const saveStepProgress = async (stepData) => {
    try {
      await saveProgress({
        step: currentStep,
        data: stepData,
        timestamp: new Date().toISOString(),
        type: 'full_onboarding'
      });
      console.log('Progress saved for step', currentStep);
    } catch (error) {
      console.warn('Failed to save progress:', error);
    }
  };

  // Handle step data changes and save progress
  const handleStepData = async (newData) => {
    const updatedFormData = {
      ...formData,
      ...newData
    };
    
    setFormData(updatedFormData);
    
    // Save progress when data changes
    await saveStepProgress(updatedFormData);
    
    // Mark step as completed if valid
    const currentStepData = ONBOARDING_STEPS[currentStep];
    if (!currentStepData.validation || currentStepData.validation(updatedFormData)) {
      setCompletedSteps(prev => new Set([...prev, currentStep]));
      setStepErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[currentStep];
        return newErrors;
      });
    }
  };

  // Get previous valid step index
  const getPreviousStepIndex = (fromIndex) => {
    for (let i = fromIndex - 1; i >= 0; i--) {
      if (shouldShowStep(i)) {
        return i;
      }
    }
    return 0;
  };

  // Enhanced step navigation with validation
  const handleNextStep = () => {
    const currentStepData = ONBOARDING_STEPS[currentStep];
    
    // Validate current step if validation exists
    if (currentStepData.validation && !validateCurrentStep()) {
      console.warn('Current step validation failed');
      return;
    }

    const nextStepIndex = getNextStepIndex(currentStep);
    if (nextStepIndex > currentStep) {
      setCurrentStep(nextStepIndex);
    }
  };

  const handlePreviousStep = () => {
    const previousStepIndex = getPreviousStepIndex(currentStep);
    if (previousStepIndex < currentStep) {
      setCurrentStep(previousStepIndex);
    }
  };

  // Smart step jumping
  const handleJumpToStep = (stepIndex) => {
    if (stepIndex < currentStep || shouldShowStep(stepIndex)) {
      setCurrentStep(stepIndex);
    }
  };

  // Smart form data suggestions based on previous answers
  const getSmartSuggestions = (stepId) => {
    switch (stepId) {
      case 'preferences':
        // Suggest learning styles based on experience level
        if (formData.experience_level === 'complete_beginner') {
          return {
            suggestedStyles: ['visual', 'hands_on', 'videos'],
            suggestedPace: 'slow'
          };
        } else if (formData.experience_level === 'advanced') {
          return {
            suggestedStyles: ['reading', 'interactive'],
            suggestedPace: 'fast'
          };
        }
        break;
      
      case 'availability':
        // Suggest platforms based on learning goals
        const techGoals = formData.learning_goals?.filter(goal => 
          ['web_dev', 'mobile_dev', 'ai_ml', 'data_science', 'devops', 'languages'].includes(goal)
        ) || [];
        
        if (techGoals.length > 0) {
          return {
            suggestedPlatforms: ['udemy', 'coursera', 'pluralsight'],
            suggestedContentTypes: ['video', 'interactive', 'project']
          };
        }
        break;
    }
    return {};
  };

  // Handle onboarding completion with API integration
  const handleComplete = async () => {
    setIsLoading(true);
    try {
      console.log('Starting full onboarding submission with data:', formData);

      // Add submission timestamp
      const submissionData = {
        ...formData,
        _startTime: formData._startTime || Date.now() - 300000,
        _completionTime: Date.now()
      };

      // Submit onboarding data using RTK Query
      const result = await submitOnboarding({
        learning_goals: submissionData.learning_goals || [],
        experience_level: submissionData.experience_level || '',
        preferred_pace: submissionData.preferred_pace || '',
        time_availability: submissionData.time_availability || '',
        learning_style: submissionData.learning_style || [],
        career_stage: submissionData.career_stage || '',
        target_timeline: submissionData.target_timeline || '',
        preferred_platforms: submissionData.preferred_platforms || [],
        content_types: submissionData.content_types || [],
        language_preference: submissionData.language_preference || ['english']
      }).unwrap();

      console.log('Full onboarding completed successfully:', result);
      
      // Manually invalidate the preferences cache to ensure fresh data
      dispatch(preferencesApi.util.invalidateTags(['UserPreferences']));
      
      // Additional cache refresh to ensure components get updated data
      setTimeout(() => {
        dispatch(preferencesApi.endpoints.getUserPreferences.initiate(undefined, { forceRefetch: true }));
      }, 100);

      // Track completion
      await trackCompletion(submissionData);
      
      // Show success message
      toast.success('Welcome to Gradvy! Your personalized learning experience is ready.');
      
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      console.error('Full onboarding submission error:', error);
      console.error('Error details:', {
        status: error?.status,
        data: error?.data,
        message: error?.message
      });
      
      const errorMessage = error?.message || error?.data?.message || error?.data?.error || 'Failed to save your preferences. Please try again.';
      
      setStepErrors(prev => ({
        ...prev,
        [currentStep]: errorMessage
      }));
      
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper functions for data transformation
  const getDifficultyPreference = (experienceLevel) => {
    switch (experienceLevel) {
      case 'complete_beginner': return 'beginner';
      case 'some_basics': return 'mixed';
      case 'intermediate': return 'intermediate';
      case 'advanced': return 'advanced';
      default: return 'mixed';
    }
  };

  const getDurationPreference = (timeAvailability) => {
    switch (timeAvailability) {
      case '1-2hrs': return 'short';
      case '3-5hrs': return 'medium';
      case '5+hrs': return 'long';
      default: return 'mixed';
    }
  };

  const trackCompletion = async (data) => {
    try {
      await fetch('/api/preferences/interactions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: JSON.stringify({
          type: 'onboarding_flow_completed',
          data: {
            total_time: data._completionTime - data._startTime,
            steps_completed: completedSteps.size,
            errors_encountered: Object.keys(stepErrors).length,
          },
          context: {
            completed_at: new Date().toISOString(),
            completion_rate: (completedSteps.size / ONBOARDING_STEPS.length) * 100,
          }
        })
      });
    } catch (error) {
      console.warn('Failed to track completion:', error);
    }
  };

  // Get current step component
  const currentStepData = ONBOARDING_STEPS[currentStep];
  const StepComponent = currentStepData.component;

  // Animation variants for step transitions
  const stepVariants = {
    enter: {
      x: 1000,
      opacity: 0
    },
    center: {
      zIndex: 1,
      x: 0,
      opacity: 1
    },
    exit: {
      zIndex: 0,
      x: -1000,
      opacity: 0
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header with progress */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              {currentStep > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handlePreviousStep}
                  className="flex items-center space-x-2"
                >
                  <ArrowLeft className="h-4 w-4" />
                  <span>Back</span>
                </Button>
              )}
            </div>
            
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {currentStepData.title}
              </h1>
              <p className="text-lg text-gray-600 mb-1">
                Complete Profile Setup
              </p>
              <p className="text-sm text-gray-500">
                Step {currentStep + 1} of {ONBOARDING_STEPS.length} • Get the most personalized experience
              </p>
              
              {currentStep === 0 && (
                <div className="mt-4 bg-white/80 backdrop-blur-sm p-4 rounded-lg inline-block">
                  <p className="text-sm text-gray-700">
                    🎯 Comprehensive setup • 📊 Detailed preferences • ⭐ Best recommendations
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Already have basic preferences?{' '}
                    <button 
                      onClick={() => router.push('/quick-onboarding')}
                      className="text-blue-600 hover:text-blue-700 underline"
                    >
                      Try quick setup instead
                    </button>
                  </p>
                </div>
              )}
            </div>
            
            <div className="w-20"></div> {/* Spacer for centering */}
          </div>
          
          {/* Smart progress bar with completion tracking */}
          <div className="space-y-2">
            <Progress value={progressPercentage} className="h-2" />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Getting Started</span>
              <div className="flex items-center space-x-2">
                {isSaving && (
                  <div className="flex items-center space-x-1">
                    <span className="animate-spin">💾</span>
                    <span>Saving...</span>
                  </div>
                )}
                <span>{Math.round(progressPercentage)}% Complete</span>
                <span>•</span>
                <span>{completedSteps.size - 1}/{ONBOARDING_STEPS.length - 1} Steps</span>
                {Object.keys(stepErrors).length > 0 && (
                  <>
                    <span>•</span>
                    <span className="text-red-500">{Object.keys(stepErrors).length} Error{Object.keys(stepErrors).length > 1 ? 's' : ''}</span>
                  </>
                )}
              </div>
              <span>Ready to Learn</span>
            </div>
          </div>
        </div>

        {/* Main onboarding content */}
        <div className="max-w-4xl mx-auto">
          <Card className="border-0 shadow-xl bg-white/80 backdrop-blur">
            <CardHeader className="pb-6">
              {/* Enhanced step indicators with completion status */}
              <div className="flex justify-center space-x-2 mb-4">
                {ONBOARDING_STEPS.map((step, index) => {
                  const isCompleted = completedSteps.has(index);
                  const isCurrent = index === currentStep;
                  const hasError = stepErrors[index];
                  
                  return (
                    <div
                      key={step.id}
                      onClick={() => handleJumpToStep(index)}
                      className={`w-4 h-4 rounded-full transition-all duration-300 cursor-pointer flex items-center justify-center ${
                        hasError
                          ? 'bg-red-500 ring-2 ring-red-200'
                          : isCompleted
                          ? 'bg-green-500 hover:bg-green-600'
                          : isCurrent
                          ? 'bg-blue-500 ring-2 ring-blue-200'
                          : 'bg-gray-200 hover:bg-gray-300'
                      }`}
                      title={`${step.title}${isCompleted ? ' ✓' : ''}${hasError ? ' ⚠' : ''}`}
                    >
                      {isCompleted && (
                        <CheckCircle className="h-2.5 w-2.5 text-white" />
                      )}
                      {hasError && !isCompleted && (
                        <span className="text-white text-xs font-bold">!</span>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardHeader>
            
            <CardContent className="min-h-[500px]">
              {/* Animated step content */}
              <AnimatePresence mode="wait">
                <motion.div
                  key={currentStep}
                  variants={stepVariants}
                  initial="enter"
                  animate="center"
                  exit="exit"
                  transition={{
                    x: { type: "spring", stiffness: 300, damping: 30 },
                    opacity: { duration: 0.2 }
                  }}
                  className="w-full"
                >
                  <StepComponent
                    data={formData}
                    onDataChange={handleStepData}
                    onNext={handleNextStep}
                    onComplete={handleComplete}
                    isLoading={isLoading || isSubmitting}
                    isSaving={isSaving}
                    currentStep={currentStep}
                    totalSteps={ONBOARDING_STEPS.length}
                    smartSuggestions={getSmartSuggestions(currentStepData.id)}
                    stepErrors={stepErrors[currentStep]}
                    isStepCompleted={completedSteps.has(currentStep)}
                    canProceed={currentStepData.validation ? validateCurrentStep() : true}
                  />
                </motion.div>
              </AnimatePresence>
            </CardContent>
          </Card>
        </div>

        {/* Help text */}
        <div className="max-w-4xl mx-auto mt-8 text-center">
          <p className="text-sm text-gray-500">
            Need help? Contact our support team at{' '}
            <a href="mailto:support@gradvy.com" className="text-blue-600 hover:underline">
              support@gradvy.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}