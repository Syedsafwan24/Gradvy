'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSelector, useDispatch } from 'react-redux';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowRight, CheckCircle, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';

import QuickOnboardingStep from '@/components/onboarding/QuickOnboardingStep';
import { useSubmitQuickOnboardingMutation, preferencesApi } from '@/services/preferencesApi';
import { loadOnboardingProgress, saveOnboardingStep, clearOnboardingProgress } from '@/utils/onboardingProgressStore';
import { normalizeApiError } from '@/utils/apiErrors';

export default function QuickOnboardingPage() {
  const router = useRouter();
  const dispatch = useDispatch();
  const { user, isAuthenticated } = useSelector(state => state.auth);
  
  const [submitQuickOnboarding, { isLoading, error }] = useSubmitQuickOnboardingMutation();
  const [isCompleted, setIsCompleted] = useState(false);
  const [formData, setFormData] = useState({
    primary_learning_goal: '',
    experience_level: '',
    time_availability: '',
    primary_learning_style: ''
  });

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login?redirect=/quick-onboarding');
    } else {
      try {
        const draft = loadOnboardingProgress(user?.id, 'quick');
        if (draft && draft.data) {
          setFormData(prev => ({ ...prev, ...draft.data }));
        }
      } catch {}
    }
  }, [isAuthenticated, router]);

  // Handle data changes from the quick onboarding step
  const handleDataChange = (newData) => {
    setFormData(prev => {
      const next = { ...prev, ...newData };
      try { saveOnboardingStep(user?.id, 'quick', 0, next); } catch {}
      return next;
    });
  };

  // Handle quick onboarding completion
  const handleComplete = async () => {
    try {
        quick_onboarding_data: {
          primary_learning_goal: formData.primary_learning_goal,
          experience_level: formData.experience_level,
          time_availability: formData.time_availability,
          primary_learning_style: formData.primary_learning_style,
          completion_time: new Date().toISOString()
        },
        basic_info: {
          learning_goals: formData.primary_learning_goal ? [formData.primary_learning_goal] : [],
          experience_level: formData.experience_level,
          time_availability: formData.time_availability,
          learning_style: formData.primary_learning_style ? [formData.primary_learning_style] : [],
          preferred_pace: getDefaultPace(formData.experience_level)
        }
      });

      // Submit quick onboarding data using RTK Query
      const result = await submitQuickOnboarding({
        quick_onboarding_data: {
          primary_learning_goal: formData.primary_learning_goal,
          experience_level: formData.experience_level,
          time_availability: formData.time_availability,
          primary_learning_style: formData.primary_learning_style,
          completion_time: new Date().toISOString()
        },
        basic_info: {
          learning_goals: formData.primary_learning_goal ? [formData.primary_learning_goal] : [],
          experience_level: formData.experience_level,
          time_availability: formData.time_availability,
          learning_style: formData.primary_learning_style ? [formData.primary_learning_style] : [],
          preferred_pace: getDefaultPace(formData.experience_level)
        }
      }).unwrap();

      
      // Invalidate the preferences cache immediately to ensure fresh data
      dispatch(preferencesApi.util.invalidateTags(['UserPreferences']));

      toast.success(result.message || 'Quick onboarding completed successfully!');
      setIsCompleted(true);
      // Clear local draft after completion - completion tracked by backend
      clearOnboardingProgress(user?.id, 'quick');
      
      // Redirect to dashboard after a brief celebration
      setTimeout(() => {
        router.push('/app/dashboard');
      }, 2000);
      
    } catch (error) {
      const e = normalizeApiError(error);
      toast.error(e.message || 'Failed to complete quick onboarding');
      
      // On error, still redirect to dashboard but show appropriate error
      setTimeout(() => {
        router.push('/app/dashboard');
      }, 1500);
    }
  };

  // Handle skip - go directly to dashboard
  const handleSkip = () => {
    router.push('/app/dashboard');
  };

  // Helper function to set default pace based on experience
  const getDefaultPace = (experienceLevel) => {
    switch (experienceLevel) {
      case 'complete_beginner': return 'slow';
      case 'some_basics': return 'medium';
      case 'intermediate': return 'fast';
      default: return 'medium';
    }
  };

  // Show loading state while checking authentication
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Show completion celebration
  if (isCompleted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          className="text-center space-y-6 max-w-md mx-auto px-4"
        >
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="flex justify-center"
          >
            <div className="w-24 h-24 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
              <CheckCircle className="h-12 w-12 text-white" />
            </div>
          </motion.div>
          
          <div className="space-y-3">
            <h2 className="text-3xl font-bold text-gray-900">
              You're all set! 🎉
            </h2>
            <p className="text-lg text-gray-600">
              We've personalized your experience based on your preferences. 
              Redirecting you to your dashboard...
            </p>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-blue-50 p-4 rounded-lg"
          >
            <div className="flex items-center justify-center space-x-2">
              <Sparkles className="h-5 w-5 text-blue-600" />
              <span className="text-blue-800 font-medium">
                Getting your personalized recommendations ready...
              </span>
            </div>
          </motion.div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <h1 className="text-4xl font-bold text-gray-900 mb-3">
                Welcome to Gradvy! 👋
              </h1>
              <p className="text-lg text-gray-600 mb-6">
                Let's quickly personalize your learning experience
              </p>
              <div className="bg-white/90 backdrop-blur-sm p-6 rounded-xl inline-block shadow-lg">
                <div className="flex items-center justify-center space-x-6 text-sm">
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">⚡</span>
                    <span className="text-gray-700 font-medium">2 minutes</span>
                  </div>
                  <div className="w-px h-6 bg-gray-300"></div>
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">🎯</span>
                    <span className="text-gray-700 font-medium">4 questions</span>
                  </div>
                  <div className="w-px h-6 bg-gray-300"></div>
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">🔄</span>
                    <span className="text-gray-700 font-medium">Customize later</span>
                  </div>
                </div>
              </div>
              
              <div className="mt-6">
                <p className="text-sm text-gray-500">
                  Want more detailed setup?{' '}
                  <button 
                    onClick={() => router.push('/onboarding')}
                    className="text-blue-600 hover:text-blue-700 underline"
                  >
                    Try full onboarding instead
                  </button>
                </p>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          <Card className="border-0 shadow-xl bg-white/80 backdrop-blur">
            <CardHeader className="pb-6">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-900">
                  Quick Setup
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  4 quick questions to get you started
                </p>
              </div>
            </CardHeader>
            
            <CardContent>
              <QuickOnboardingStep
                data={formData}
                onDataChange={handleDataChange}
                onComplete={handleComplete}
                onSkip={handleSkip}
                isLoading={isLoading}
              />
            </CardContent>
          </Card>
        </div>

        {/* Value Proposition */}
        <div className="max-w-4xl mx-auto mt-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="bg-white/60 backdrop-blur-sm p-6 rounded-xl"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
              Why personalize your experience?
            </h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="w-12 h-12 mx-auto bg-blue-100 rounded-lg flex items-center justify-center mb-3">
                  <span className="text-2xl">🎯</span>
                </div>
                <h4 className="font-medium text-gray-900">Better Recommendations</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Get courses that match your goals and skill level
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 mx-auto bg-green-100 rounded-lg flex items-center justify-center mb-3">
                  <span className="text-2xl">⚡</span>
                </div>
                <h4 className="font-medium text-gray-900">Faster Learning</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Content tailored to your preferred learning style
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 mx-auto bg-purple-100 rounded-lg flex items-center justify-center mb-3">
                  <span className="text-2xl">📈</span>
                </div>
                <h4 className="font-medium text-gray-900">Track Progress</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Monitor your learning journey effectively
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Help Text */}
        <div className="max-w-4xl mx-auto mt-6 text-center">
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
