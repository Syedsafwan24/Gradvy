'use client';

import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Settings, 
  User, 
  BookOpen, 
  Clock, 
  Target, 
  TrendingUp,
  Edit,
  Save,
  X,
  Plus,
  Trash2,
  RefreshCw,
  Download,
  Upload,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import PreferencesOverview from '@/components/preferences/PreferencesOverview';
import LearningGoalsManager from '@/components/preferences/LearningGoalsManager';
import ContentPreferences from '@/components/preferences/ContentPreferences';
import LearningHistory from '@/components/preferences/LearningHistory';
import RecommendationSettings from '@/components/preferences/RecommendationSettings';
import AnalyticsInsights from '@/components/preferences/AnalyticsInsights';
import {
  useGetUserPreferencesQuery,
  usePartialUpdateUserPreferencesMutation,
  useGetUserAnalyticsQuery,
  useGetPersonalizedRecommendationsQuery,
  logUserInteraction,
  transformPreferenceData,
  calculatePreferenceCompletion
} from '@/services/preferencesApi';
import usePreferencesValidation from '@/hooks/usePreferencesValidation';

export default function PreferencesPage() {
  const { user, isAuthenticated } = useSelector(state => state.auth);
  const dispatch = useDispatch();
  const [activeTab, setActiveTab] = useState('overview');
  const [hasChanges, setHasChanges] = useState(false);
  const [lastSaved, setLastSaved] = useState(null);

  // RTK Query hooks
  const {
    data: userPreferences,
    isLoading: loading,
    error: preferencesError,
    refetch: refetchPreferences
  } = useGetUserPreferencesQuery(undefined, {
    skip: !isAuthenticated || !user,
    refetchOnMountOrArgChange: true
  });

  const {
    data: analyticsData,
    isLoading: analyticsLoading,
    refetch: refetchAnalytics
  } = useGetUserAnalyticsQuery('30d', {
    skip: !userPreferences || !isAuthenticated
  });

  const {
    data: recommendationsData,
    isLoading: recommendationsLoading,
    refetch: refetchRecommendations
  } = useGetPersonalizedRecommendationsQuery(undefined, {
    skip: !userPreferences || !isAuthenticated
  });

  const [updatePreferences, { 
    isLoading: saving, 
    error: saveError 
  }] = usePartialUpdateUserPreferencesMutation();

  // Real-time validation
  const validation = usePreferencesValidation(userPreferences, {
    enableRealTime: true,
    debounceMs: 500
  });

  // Log page view interaction
  useEffect(() => {
    if (isAuthenticated && user) {
      logUserInteraction(dispatch, 'page_view', {
        page: 'preferences_dashboard',
        tab: activeTab
      });
    }
  }, [isAuthenticated, user, activeTab, dispatch]);

  const handlePreferenceChange = async (section, updatedData) => {
    try {
      setHasChanges(true);
      
      // Validate the updated data first
      const testPreferences = {
        ...userPreferences,
        [section]: {
          ...userPreferences?.[section],
          ...updatedData
        }
      };

      // Trigger field-level validation for changed fields
      Object.keys(updatedData).forEach(fieldName => {
        validation.validateField(section, fieldName, updatedData[fieldName]);
      });

      // Don't save if validation fails for critical fields
      const sectionValidation = validation.getSectionValidation(section);
      if (section === 'basic_info' && sectionValidation.hasErrors) {
        // For basic info, show validation errors but still allow saving
        toast.error('Please fix validation errors before saving', {
          duration: 4000,
          icon: <AlertCircle className="w-4 h-4" />
        });
        return;
      }
      
      // Transform the data to match backend schema
      const transformedData = transformPreferenceData({
        [section]: updatedData
      });

      // Update preferences via RTK Query
      const result = await updatePreferences(transformedData).unwrap();
      
      setLastSaved(new Date());
      setHasChanges(false);
      
      // Show success toast with validation info
      const validationSummary = validation.summary;
      toast.success(
        `Preferences saved! ${validationSummary?.completionPercentage || 0}% complete`, 
        {
          duration: 3000,
          icon: <CheckCircle className="w-4 h-4" />
        }
      );

      // Log the preference change interaction
      logUserInteraction(dispatch, 'page_view', {
        section: section,
        changes: Object.keys(updatedData),
        validation_state: validation.isValid,
        completion_percentage: validationSummary?.completionPercentage || 0,
        timestamp: new Date().toISOString()
      }, {
        page: 'preferences_dashboard',
        action: 'preference_update'
      });

    } catch (error) {
      console.error('Failed to save preferences:', error);
      toast.error(error?.message || 'Failed to save preferences. Please try again.', {
        duration: 5000,
        icon: <AlertCircle className="w-4 h-4" />
      });
    }
  };

  const exportPreferences = async () => {
    try {
      const dataStr = JSON.stringify(userPreferences, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `gradvy-preferences-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      URL.revokeObjectURL(url);
      
      // Log export interaction
      logUserInteraction(dispatch, 'preferences_exported', {
        export_date: new Date().toISOString(),
        total_preferences: Object.keys(userPreferences).length
      });
      
      toast.success('Preferences exported successfully!');
    } catch (error) {
      console.error('Failed to export preferences:', error);
      toast.error('Failed to export preferences.');
    }
  };

  const resetToOnboarding = async () => {
    if (window.confirm('Are you sure you want to reset your preferences? This will take you back to the onboarding flow.')) {
      try {
        // Log reset interaction
        logUserInteraction(dispatch, 'preferences_reset', {
          reset_date: new Date().toISOString(),
        });
        
        // Redirect to onboarding (preferences will be recreated there)
        window.location.href = '/onboarding';
      } catch (error) {
        console.error('Failed to reset preferences:', error);
        toast.error('Failed to reset preferences.');
      }
    }
  };


  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  };

  return (
    <ProtectedRoute requireAuth={true} redirectTo="/login">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50"
      >
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <motion.div variants={itemVariants} className="mb-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                  <Settings className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">Learning Preferences</h1>
                  <p className="text-gray-600">Manage your personalized learning experience</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                {saving && (
                  <div className="flex items-center space-x-2 text-blue-600">
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Saving...</span>
                  </div>
                )}
                
                {lastSaved && !hasChanges && (
                  <div className="flex items-center space-x-2 text-green-600">
                    <CheckCircle className="h-4 w-4" />
                    <span className="text-sm">
                      Saved {lastSaved.toLocaleTimeString()}
                    </span>
                  </div>
                )}
                
                {userPreferences && (
                  <div className="flex items-center space-x-2">
                    <Badge 
                      variant="outline" 
                      className={`${validation.isValid ? 'text-green-600 border-green-200' : 'text-orange-600 border-orange-200'}`}
                    >
                      {validation.completionPercentage}% Complete
                    </Badge>
                    {!validation.isValid && validation.suggestions.length > 0 && (
                      <Badge variant="outline" className="text-orange-600 border-orange-200">
                        {validation.suggestions.length} suggestions
                      </Badge>
                    )}
                  </div>
                )}
                
                <Button
                  variant="outline"
                  onClick={() => refetchPreferences()}
                  disabled={loading}
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
                
                {userPreferences && (
                  <Button
                    variant="outline"
                    onClick={exportPreferences}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                )}
              </div>
            </div>
            
            {(saveError || preferencesError?.onboarding_required) && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`mt-4 p-4 border rounded-lg flex items-center space-x-3 ${
                  preferencesError?.onboarding_required 
                    ? 'bg-yellow-50 border-yellow-200' 
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <AlertCircle className={`h-5 w-5 flex-shrink-0 ${
                  preferencesError?.onboarding_required ? 'text-yellow-500' : 'text-red-500'
                }`} />
                <p className={preferencesError?.onboarding_required ? 'text-yellow-700' : 'text-red-700'}>
                  {preferencesError?.onboarding_required 
                    ? 'Complete onboarding to set up your preferences.'
                    : (saveError?.data?.message || saveError?.message || 'An error occurred')
                  }
                </p>
                {preferencesError?.onboarding_required && (
                  <Button
                    onClick={() => window.location.href = '/onboarding'}
                    size="sm"
                  >
                    Complete Onboarding
                  </Button>
                )}
              </motion.div>
            )}
          </motion.div>

          {/* Main Content */}
          <motion.div variants={itemVariants}>
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="grid grid-cols-6 lg:w-fit">
                <TabsTrigger value="overview" className="flex items-center space-x-2">
                  <User className="h-4 w-4" />
                  <span className="hidden sm:inline">Overview</span>
                </TabsTrigger>
                <TabsTrigger value="goals" className="flex items-center space-x-2">
                  <Target className="h-4 w-4" />
                  <span className="hidden sm:inline">Goals</span>
                </TabsTrigger>
                <TabsTrigger value="content" className="flex items-center space-x-2">
                  <BookOpen className="h-4 w-4" />
                  <span className="hidden sm:inline">Content</span>
                </TabsTrigger>
                <TabsTrigger value="history" className="flex items-center space-x-2">
                  <Clock className="h-4 w-4" />
                  <span className="hidden sm:inline">History</span>
                </TabsTrigger>
                <TabsTrigger value="recommendations" className="flex items-center space-x-2">
                  <TrendingUp className="h-4 w-4" />
                  <span className="hidden sm:inline">Recommendations</span>
                </TabsTrigger>
                <TabsTrigger value="analytics" className="flex items-center space-x-2">
                  <TrendingUp className="h-4 w-4" />
                  <span className="hidden sm:inline">Analytics</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-6">
                <PreferencesOverview
                  preferences={userPreferences}
                  loading={loading}
                  validation={validation}
                  onPreferenceChange={handlePreferenceChange}
                  onResetToOnboarding={resetToOnboarding}
                />
              </TabsContent>

              <TabsContent value="goals" className="space-y-6">
                <LearningGoalsManager
                  preferences={userPreferences}
                  loading={loading}
                  validation={validation}
                  onPreferenceChange={handlePreferenceChange}
                />
              </TabsContent>

              <TabsContent value="content" className="space-y-6">
                <ContentPreferences
                  preferences={userPreferences}
                  loading={loading}
                  validation={validation}
                  onPreferenceChange={handlePreferenceChange}
                />
              </TabsContent>

              <TabsContent value="history" className="space-y-6">
                <LearningHistory
                  preferences={userPreferences}
                  loading={loading}
                />
              </TabsContent>

              <TabsContent value="recommendations" className="space-y-6">
                <RecommendationSettings
                  preferences={userPreferences}
                  recommendations={recommendationsData}
                  loading={loading || recommendationsLoading}
                  onPreferenceChange={handlePreferenceChange}
                  onRefreshRecommendations={refetchRecommendations}
                />
              </TabsContent>

              <TabsContent value="analytics" className="space-y-6">
                <AnalyticsInsights
                  preferences={userPreferences}
                  analytics={analyticsData}
                  loading={loading || analyticsLoading}
                  onRefreshAnalytics={refetchAnalytics}
                />
              </TabsContent>
            </Tabs>
          </motion.div>
        </div>
      </motion.div>
    </ProtectedRoute>
  );
}