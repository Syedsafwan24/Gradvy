'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { useGetUserPreferencesQuery, useLogInteractionMutation } from '@/services/preferencesApi';

export const useProfileCompletionPrompts = (user) => {
  const router = useRouter();
  const [promptsEnabled, setPromptsEnabled] = useState(true);
  const promptShownRef = useRef(false);
  const lastPromptTimeRef = useRef(0);
  const currentToastRef = useRef(null);
  
  // Use RTK Query to fetch preferences
  const { 
    data: preferences, 
    isLoading,
    isError,
    error 
  } = useGetUserPreferencesQuery(undefined, {
    skip: !user || !promptsEnabled
  });
  
  const [logInteraction] = useLogInteractionMutation();
  
  // Handle case where preferences don't exist (404 or other errors)
  const effectivePreferences = (() => {
    if (isLoading) {
      return null; // Return null during loading to prevent premature prompts
    }
    
    if (isError) {
      console.log('API Error fetching preferences:', error);
      
      // Only default to incomplete state for 404 (no preferences found)
      if (error?.status === 404 || error?.originalStatus === 404) {
        console.log('No preferences found (404), defaulting to incomplete state');
        return {
          profile_completion_percentage: 0,
          onboarding_status: 'not_started'
        };
      }
      
      // For other errors (auth, network, etc), don't show prompts
      return null;
    }
    
    return preferences;
  })();

  useEffect(() => {
    if (user && promptsEnabled && effectivePreferences) {
      console.log('useProfileCompletionPrompts: Checking prompts for user', {
        user: user?.id,
        preferences: effectivePreferences,
        promptShown: promptShownRef.current
      });
      checkAndShowPrompts(effectivePreferences);
    }
  }, [user, promptsEnabled, effectivePreferences]);

  const checkAndShowPrompts = (prefs) => {
    const completionPercentage = prefs.profile_completion_percentage || 0;
    const onboardingStatus = prefs.onboarding_status || 'not_started';
    const now = Date.now();

    // Don't show prompts if onboarding is fully completed
    if (onboardingStatus === 'full_completed') {
      return;
    }

    // Don't show prompts if profile is sufficiently complete
    if (completionPercentage >= 80) {
      return;
    }

    // Prevent duplicate prompts within 10 seconds
    if (promptShownRef.current && (now - lastPromptTimeRef.current) < 10000) {
      console.log('Preventing duplicate prompt - too soon since last prompt');
      return;
    }

    // Dismiss any existing toasts before showing new one
    if (currentToastRef.current) {
      console.log('Dismissing existing toast');
      toast.dismiss(currentToastRef.current);
      currentToastRef.current = null;
    }

    // Show different prompts based on onboarding status with debounce
    const promptTimeout = setTimeout(() => {
      if (!promptShownRef.current) {
        promptShownRef.current = true;
        lastPromptTimeRef.current = now;
        
        if (onboardingStatus === 'not_started') {
          showQuickOnboardingPrompt();
        } else if (onboardingStatus === 'quick_completed' && completionPercentage < 50) {
          showFullOnboardingPrompt();
        } else if (completionPercentage < 80) {
          showProfileCompletionPrompt(completionPercentage);
        }
      }
    }, 3000); // Delay to avoid overwhelming user on page load

    // Reset prompt shown flag after timeout
    setTimeout(() => {
      promptShownRef.current = false;
    }, 15000); // Reset after 15 seconds
  };

  const showQuickOnboardingPrompt = () => {
    const toastId = toast.custom((t) => (
      <div className={`${
        t.visible ? 'animate-enter' : 'animate-leave'
      } max-w-md w-full bg-white shadow-lg rounded-lg pointer-events-auto flex ring-1 ring-black ring-opacity-5`}>
        <div className="flex-1 w-0 p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <span className="text-2xl">🚀</span>
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium text-gray-900">
                Complete your quick setup
              </p>
              <p className="mt-1 text-sm text-gray-500">
                Get personalized recommendations in just 2 minutes
              </p>
            </div>
          </div>
        </div>
        <div className="flex border-l border-gray-200">
          <button
            onClick={() => {
              toast.dismiss(t.id);
              currentToastRef.current = null;
              router.push('/app/quick-onboarding');
              logPromptInteraction('quick_onboarding', 'clicked');
            }}
            className="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-blue-600 hover:text-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Setup
          </button>
        </div>
        <div className="flex border-l border-gray-200">
          <button
            onClick={() => {
              toast.dismiss(t.id);
              currentToastRef.current = null;
              logPromptInteraction('quick_onboarding', 'dismissed');
            }}
            className="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            ✕
          </button>
        </div>
      </div>
    ), {
      duration: 8000,
      position: 'top-right',
    });
    
    currentToastRef.current = toastId;
  };

  const showFullOnboardingPrompt = () => {
    const toastId = toast.custom((t) => (
      <div className={`${
        t.visible ? 'animate-enter' : 'animate-leave'
      } max-w-md w-full bg-white shadow-lg rounded-lg pointer-events-auto flex ring-1 ring-black ring-opacity-5`}>
        <div className="flex-1 w-0 p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <span className="text-2xl">🎯</span>
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium text-gray-900">
                Complete your learning profile
              </p>
              <p className="mt-1 text-sm text-gray-500">
                Unlock better course recommendations
              </p>
            </div>
          </div>
        </div>
        <div className="flex border-l border-gray-200">
          <button
            onClick={() => {
              toast.dismiss(t.id);
              currentToastRef.current = null;
              router.push('/app/onboarding');
              logPromptInteraction('full_onboarding', 'clicked');
            }}
            className="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-blue-600 hover:text-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Complete
          </button>
        </div>
        <div className="flex border-l border-gray-200">
          <button
            onClick={() => {
              toast.dismiss(t.id);
              currentToastRef.current = null;
              logPromptInteraction('full_onboarding', 'dismissed');
            }}
            className="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            ✕
          </button>
        </div>
      </div>
    ), {
      duration: 6000,
      position: 'top-right',
    });
    
    currentToastRef.current = toastId;
  };

  const showProfileCompletionPrompt = (completionPercentage) => {
    const messages = [
      {
        emoji: '📈',
        title: 'Enhance your profile',
        description: `You're ${Math.round(completionPercentage)}% complete! Add more details for better recommendations.`
      },
      {
        emoji: '⭐',
        title: 'Almost there!',
        description: `${100 - Math.round(completionPercentage)}% left to unlock full personalization.`
      },
      {
        emoji: '🎨',
        title: 'Personalize your experience',
        description: 'Update your preferences for more relevant content.'
      }
    ];

    const message = messages[Math.floor(Math.random() * messages.length)];

    const toastId = toast.custom((t) => (
      <div className={`${
        t.visible ? 'animate-enter' : 'animate-leave'
      } max-w-md w-full bg-white shadow-lg rounded-lg pointer-events-auto flex ring-1 ring-black ring-opacity-5`}>
        <div className="flex-1 w-0 p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <span className="text-2xl">{message.emoji}</span>
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium text-gray-900">
                {message.title}
              </p>
              <p className="mt-1 text-sm text-gray-500">
                {message.description}
              </p>
            </div>
          </div>
        </div>
        <div className="flex border-l border-gray-200">
          <button
            onClick={() => {
              toast.dismiss(t.id);
              currentToastRef.current = null;
              router.push('/app/preferences');
              logPromptInteraction('profile_completion', 'clicked');
            }}
            className="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-blue-600 hover:text-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Update
          </button>
        </div>
        <div className="flex border-l border-gray-200">
          <button
            onClick={() => {
              toast.dismiss(t.id);
              currentToastRef.current = null;
              logPromptInteraction('profile_completion', 'dismissed');
            }}
            className="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            ✕
          </button>
        </div>
      </div>
    ), {
      duration: 5000,
      position: 'top-right',
    });
    
    currentToastRef.current = toastId;
  };

  const logPromptInteraction = async (promptType, action) => {
    try {
      await logInteraction({
        type: 'page_view',
        data: {
          prompt_type: promptType,
          action: action,
          timestamp: new Date().toISOString(),
          completion_percentage: effectivePreferences?.profile_completion_percentage || 0,
          page: 'completion_prompt'
        },
        context: {
          source: 'toast_notification',
          page: window.location.pathname,
          interaction_type: 'completion_prompt_interaction'
        }
      }).unwrap();
    } catch (error) {
      console.error('Error logging prompt interaction:', error);
    }
  };

  const showSuccessToast = useCallback((message, type = 'success') => {
    const toasts = {
      quick_onboarding: {
        emoji: '🎉',
        title: 'Quick setup complete!',
        description: 'Your personalized experience is ready.'
      },
      full_onboarding: {
        emoji: '✅',
        title: 'Profile complete!',
        description: 'You\'ll now get the best recommendations.'
      },
      profile_updated: {
        emoji: '🔄',
        title: 'Profile updated!',
        description: 'Your preferences have been saved.'
      }
    };

    const toastContent = toasts[type] || {
      emoji: '✅',
      title: 'Success!',
      description: message
    };

    toast.custom((t) => (
      <div className={`${
        t.visible ? 'animate-enter' : 'animate-leave'
      } max-w-md w-full bg-green-50 shadow-lg rounded-lg pointer-events-auto flex ring-1 ring-green-200`}>
        <div className="flex-1 w-0 p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <span className="text-2xl">{toastContent.emoji}</span>
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium text-green-900">
                {toastContent.title}
              </p>
              <p className="mt-1 text-sm text-green-700">
                {toastContent.description}
              </p>
            </div>
          </div>
        </div>
      </div>
    ), {
      duration: 4000,
      position: 'top-right',
    });
  }, []);

  const disablePrompts = useCallback(() => {
    setPromptsEnabled(false);
  }, []);

  const enablePrompts = useCallback(() => {
    setPromptsEnabled(true);
  }, []);

  return {
    preferences: effectivePreferences,
    showSuccessToast,
    disablePrompts,
    enablePrompts,
    promptsEnabled
  };
};