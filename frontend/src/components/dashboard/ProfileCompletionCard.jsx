'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  CheckCircle, 
  ArrowRight, 
  User, 
  Target, 
  Clock,
  BookOpen,
  Sparkles,
  X,
  Star,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useGetUserPreferencesQuery, useLogInteractionMutation } from '@/services/preferencesApi';

export default function ProfileCompletionCard({ 
  user, 
  onDismiss,
  forceShow = false
}) {
  const router = useRouter();
  const [dismissed, setDismissed] = useState(false);
  
  // Use RTK Query to fetch user preferences
  const { 
    data: preferences, 
    isLoading: loading, 
    error,
    isError 
  } = useGetUserPreferencesQuery();
  
  const [logInteraction] = useLogInteractionMutation();
  
  // Handle case where preferences don't exist (404 or error)
  const effectivePreferences = isError ? {
    profile_completion_percentage: 0,
    onboarding_completed: false,
    quick_onboarding_completed: false
  } : preferences;

  const handleDismiss = async () => {
    try {
      // Use RTK Query to log dismissal interaction - continue even if this fails
      await logInteraction({
        type: 'page_view',
        data: {
          dismissed_at: new Date().toISOString(),
          completion_percentage: effectivePreferences?.profile_completion_percentage || 0,
          page: 'completion_prompt',
          action: 'dismissed'
        },
        context: {
          source: 'dashboard_completion_card',
          interaction_type: 'completion_prompt_dismissed'
        }
      }).unwrap();
    } catch (error) {
      // Silently fail interaction logging - don't block user experience
      console.warn('Failed to log interaction (non-critical):', error);
    }
    
    setDismissed(true);
    if (onDismiss) {
      onDismiss();
    }
  };

  const handleQuickOnboarding = () => {
    router.push('/app/quick-onboarding');
  };

  const handleFullOnboarding = () => {
    router.push('/app/onboarding');
  };

  const handleCompleteProfile = () => {
    router.push('/app/preferences');
  };

  // Don't show if dismissed and not forced
  if (dismissed && !forceShow) {
    return null;
  }

  // Don't show if loading
  if (loading) {
    return null;
  }

  // Show error state if preferences API is completely down (5xx errors)
  if (isError && error?.status >= 500) {
    return (
      <Card className="border-yellow-200 bg-yellow-50">
        <div className="p-4 text-center">
          <AlertCircle className="h-6 w-6 text-yellow-600 mx-auto mb-2" />
          <p className="text-sm text-yellow-800">
            Having trouble loading your profile data. You can still use the app normally.
          </p>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => window.location.reload()} 
            className="mt-2 text-yellow-700 border-yellow-300 hover:bg-yellow-100"
          >
            Try Again
          </Button>
        </div>
      </Card>
    );
  }

  // Don't show if profile is sufficiently complete (>= 80%) and not forced
  const completionPercentage = effectivePreferences?.profile_completion_percentage || 0;
  if (completionPercentage >= 80 && !forceShow) {
    return null;
  }

  // Determine the card content based on completion status
  const getCardContent = () => {
    if (!effectivePreferences?.quick_onboarding_completed) {
      // Haven't done quick onboarding yet
      return {
        title: "Welcome to Gradvy! 👋",
        description: "Let's quickly personalize your learning experience with 4 simple questions.",
        primaryAction: "Complete Quick Setup (2 min)",
        primaryHandler: handleQuickOnboarding,
        secondaryAction: "Skip for now",
        secondaryHandler: handleDismiss,
        icon: Sparkles,
        gradient: "from-blue-500 to-purple-600",
        urgency: "high"
      };
    } else if (!effectivePreferences?.onboarding_completed) {
      // Done quick onboarding but not full onboarding
      return {
        title: "Complete Your Learning Profile",
        description: `Your profile is ${Math.round(completionPercentage)}% complete. Unlock better recommendations by completing your full profile.`,
        primaryAction: "Complete Full Profile",
        primaryHandler: handleFullOnboarding,
        secondaryAction: "Update Preferences",
        secondaryHandler: handleCompleteProfile,
        icon: Target,
        gradient: "from-green-500 to-blue-600",
        urgency: "medium"
      };
    } else {
      // Full onboarding complete but profile not 100%
      return {
        title: "Enhance Your Profile",
        description: `Your profile is ${Math.round(completionPercentage)}% complete. Add more details for even better personalization.`,
        primaryAction: "Update Preferences",
        primaryHandler: handleCompleteProfile,
        secondaryAction: null,
        secondaryHandler: null,
        icon: Star,
        gradient: "from-purple-500 to-pink-600",
        urgency: "low"
      };
    }
  };

  const cardContent = getCardContent();
  const IconComponent = cardContent.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className={`p-6 border-2 ${
        cardContent.urgency === 'high' ? 'border-blue-200 bg-gradient-to-br from-blue-50 to-purple-50' :
        cardContent.urgency === 'medium' ? 'border-green-200 bg-gradient-to-br from-green-50 to-blue-50' :
        'border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50'
      }`}>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${cardContent.gradient} flex items-center justify-center`}>
              <IconComponent className="h-6 w-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">
                {cardContent.title}
              </h3>
              <p className="text-gray-600 mt-1">
                {cardContent.description}
              </p>
            </div>
          </div>
          
          {!forceShow && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDismiss}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>

        {/* Progress Bar */}
        {completionPercentage > 0 && (
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Profile Completion</span>
              <span className="text-sm text-gray-600">{Math.round(completionPercentage)}%</span>
            </div>
            <Progress 
              value={completionPercentage} 
              className="h-3"
            />
          </div>
        )}

        {/* Benefits */}
        <div className="mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="flex items-center space-x-2 text-sm">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-gray-700">Better recommendations</span>
            </div>
            <div className="flex items-center space-x-2 text-sm">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-gray-700">Personalized content</span>
            </div>
            <div className="flex items-center space-x-2 text-sm">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-gray-700">Track your progress</span>
            </div>
          </div>
        </div>

        {/* Completion Status Badges */}
        {(effectivePreferences?.quick_onboarding_completed || effectivePreferences?.onboarding_completed) && (
          <div className="flex flex-wrap gap-2 mb-4">
            {effectivePreferences?.quick_onboarding_completed && (
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                ✓ Quick Setup Complete
              </Badge>
            )}
            {effectivePreferences?.onboarding_completed && (
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                ✓ Full Profile Complete
              </Badge>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          <Button
            onClick={cardContent.primaryHandler}
            className={`bg-gradient-to-r ${cardContent.gradient} hover:opacity-90 text-white flex-1`}
          >
            {cardContent.primaryAction}
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
          
          {cardContent.secondaryAction && (
            <Button
              variant="outline"
              onClick={cardContent.secondaryHandler}
              className="flex-1 sm:flex-none"
            >
              {cardContent.secondaryAction}
            </Button>
          )}
        </div>
      </Card>
    </motion.div>
  );
}