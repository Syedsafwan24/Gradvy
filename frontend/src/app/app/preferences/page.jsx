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
  calculatePreferenceCompletion,
  updatePreferencesWithRetry,
  preferencesDebugUtils,
  validatePreferencesData
} from '@/services/preferencesApi';
import usePreferencesValidation from '@/hooks/usePreferencesValidation';

export default function PreferencesPage() {
  const { user, isAuthenticated } = useSelector(state => state.auth);
  const dispatch = useDispatch();
  const [activeTab, setActiveTab] = useState('overview');
  const [hasChanges, setHasChanges] = useState(false);
  const [lastSaved, setLastSaved] = useState(null);

  // Local state for tracking unsaved changes
  const [localChanges, setLocalChanges] = useState({});
  const [isDirty, setIsDirty] = useState(false);

  // RTK Query hooks
  const {
    data: userPreferences,
    isLoading: loading,
    error: preferencesError,
    refetch: refetchPreferences,
    isFetching,
    isSuccess,
    isError,
    originalArgs,
    endpointName,
    requestId,
    startedTimeStamp,
    fulfilledTimeStamp
  } = useGetUserPreferencesQuery(undefined, {
    skip: !isAuthenticated || !user,
    refetchOnMountOrArgChange: true
  });

  // Enhanced debug logging for preferences loading
  useEffect(() => {
    if (isAuthenticated && user) {
      console.log('🔍 PREFERENCES PAGE INIT - Starting preferences fetch');
      console.log('👤 User info:', { id: user?.id, username: user?.username });
    }
  }, [isAuthenticated, user]);

  // Enhanced cache debugging for RTK Query
  useEffect(() => {
    console.log('🔍 RTK QUERY STATE CHANGE:');
    console.log('   📊 Loading:', loading);
    console.log('   🔄 Fetching:', isFetching);
    console.log('   ✅ Success:', isSuccess);
    console.log('   ❌ Error:', isError);
    console.log('   🎯 Request ID:', requestId);
    console.log('   ⏱️  Started:', startedTimeStamp ? new Date(startedTimeStamp).toISOString() : 'N/A');
    console.log('   ✔️  Fulfilled:', fulfilledTimeStamp ? new Date(fulfilledTimeStamp).toISOString() : 'N/A');

    if (loading) {
      console.log('⏳ PREFERENCES LOADING - Fetching user preferences...');
    } else if (preferencesError) {
      console.error('❌ PREFERENCES ERROR - Failed to fetch preferences');
      console.error('🔍 Error details:', preferencesError);
      console.error('🔍 Error keys:', Object.keys(preferencesError || {}));
    } else if (userPreferences) {
      console.log('✅ PREFERENCES SUCCESS - Preferences loaded');
      console.log('📦 Preferences keys:', Object.keys(userPreferences));
      console.log('📊 Profile completion:', userPreferences.profile_completion_percentage);
      console.log('🏷️  Onboarding status:', userPreferences.onboarding_status);
      console.log('📋 Basic info exists:', !!userPreferences.basic_info);
      console.log('🎯 Content prefs exists:', !!userPreferences.content_preferences);

      if (userPreferences.basic_info) {
        console.log('📋 Basic info fields:', Object.keys(userPreferences.basic_info));
        console.log('🎯 Learning goals:', userPreferences.basic_info.learning_goals);
      }

      if (userPreferences.content_preferences) {
        console.log('🎯 Content pref fields:', Object.keys(userPreferences.content_preferences));
      }

      // Cache freshness check
      const cacheAge = fulfilledTimeStamp ? Date.now() - fulfilledTimeStamp : 'Unknown';
      console.log('🕐 Cache age:', typeof cacheAge === 'number' ? `${cacheAge}ms` : cacheAge);

    } else {
      console.log('❓ PREFERENCES EMPTY - No data received');
    }
  }, [loading, isFetching, isSuccess, isError, preferencesError, userPreferences, requestId, startedTimeStamp, fulfilledTimeStamp]);

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
    const loadingToastId = toast.loading('Saving preferences...', {
      icon: <RefreshCw className="w-4 h-4 animate-spin" />
    });

    try {
      setHasChanges(true);

      // Debug logging
      console.log('🔄 Starting preference update:', { section, updatedData });

      // Log current cache state (removed faulty debug call - cache is working properly)
      console.log('🔍 Cache state: RTK Query managing preferences cache automatically');

      // Validate the updated data first
      const testPreferences = {
        ...userPreferences,
        [section]: {
          ...userPreferences?.[section],
          ...updatedData
        }
      };

      // Validate preferences data structure
      const dataValidation = validatePreferencesData(testPreferences);
      if (!dataValidation.isValid) {
        console.warn('⚠️ Data validation warnings:', dataValidation.errors);
      }

      // Trigger field-level validation for changed fields
      Object.keys(updatedData).forEach(fieldName => {
        validation.validateField(section, fieldName, updatedData[fieldName]);
      });

      // Only block saves for critical validation errors (not for incomplete/partial data)
      const sectionValidation = validation.getSectionValidation(section);

      // Allow saves even with minor validation errors during editing
      // Only block for truly critical errors that would break the backend
      const hasCriticalErrors = sectionValidation.hasErrors && Object.keys(sectionValidation.errors).some(field => {
        const errors = sectionValidation.errors[field];
        return errors.some(error =>
          error.includes('required') ||
          error.includes('invalid format') ||
          error.includes('not a valid choice')
        );
      });

      if (section === 'basic_info' && hasCriticalErrors) {
        toast.dismiss(loadingToastId);
        toast.error('Please fix critical validation errors before saving', {
          duration: 4000,
          icon: <AlertCircle className="w-4 h-4" />
        });
        return;
      }

      // Transform the data to match backend schema
      const transformedData = transformPreferenceData({
        [section]: updatedData
      });

      // Validate transformation output
      preferencesDebugUtils.validateTransformOutput({ [section]: updatedData }, transformedData);

      console.log('🔄 Transformed data:', transformedData);

      // Update preferences with retry mechanism
      const result = await updatePreferencesWithRetry(transformedData, dispatch, 3);

      toast.dismiss(loadingToastId);
      setLastSaved(new Date());
      setHasChanges(false);

      // Show success toast with attempt info
      const validationSummary = validation.summary;
      const successMessage = result.attempts > 1
        ? `Preferences saved after ${result.attempts} attempts! ${validationSummary?.completionPercentage || 0}% complete`
        : `Preferences saved! ${validationSummary?.completionPercentage || 0}% complete`;

      toast.success(successMessage, {
        duration: 3000,
        icon: <CheckCircle className="w-4 h-4" />
      });

      // Log the preference change interaction
      logUserInteraction(dispatch, 'page_view', {
        section: section,
        changes: Object.keys(updatedData),
        validation_state: validation.isValid,
        completion_percentage: validationSummary?.completionPercentage || 0,
        attempts: result.attempts,
        timestamp: new Date().toISOString()
      }, {
        page: 'preferences_dashboard',
        action: 'preference_update'
      });

    } catch (error) {
      toast.dismiss(loadingToastId);
      console.error('Failed to save preferences:', error);

      const errorMessage = error?.attempts > 1
        ? `Failed to save preferences after ${error.attempts} attempts. ${error?.message || 'Please try again.'}`
        : error?.message || 'Failed to save preferences. Please try again.';

      toast.error(errorMessage, {
        duration: 5000,
        icon: <AlertCircle className="w-4 h-4" />
      });
    }
  };

  // Handle local preference changes without auto-saving
  const handleLocalPreferenceChange = (section, updatedData) => {
    console.log('🔄 Local preference change:', { section, updatedData });

    // Update local changes state
    setLocalChanges(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        ...updatedData
      }
    }));

    // Mark as dirty
    setIsDirty(true);

    // Trigger field-level validation for feedback (but don't block)
    Object.keys(updatedData).forEach(fieldName => {
      validation.validateField(section, fieldName, updatedData[fieldName]);
    });
  };

  // Manual save function - only called when user clicks Save
  const handleSaveChanges = async () => {
    if (!isDirty || Object.keys(localChanges).length === 0) {
      toast.info('No changes to save');
      return;
    }

    const loadingToastId = toast.loading('Saving preferences...', {
      icon: <RefreshCw className="w-4 h-4 animate-spin" />
    });

    try {
      console.log('💾 Saving local changes:', localChanges);

      // Process each section with changes
      for (const [section, sectionChanges] of Object.entries(localChanges)) {
        // Build full section data for validation
        const fullSectionData = {
          ...userPreferences?.[section],
          ...sectionChanges
        };

        // Check for critical validation errors before saving this section
        const testPreferences = {
          ...userPreferences,
          [section]: fullSectionData
        };

        // Validate preferences data structure
        const dataValidation = validatePreferencesData(testPreferences);
        if (!dataValidation.isValid) {
          console.warn('⚠️ Data validation warnings:', dataValidation.errors);
        }

        // Only block for critical errors that would break the backend
        const sectionValidation = validation.getSectionValidation(section);
        const hasCriticalErrors = sectionValidation.hasErrors && Object.keys(sectionValidation.errors).some(field => {
          const errors = sectionValidation.errors[field];
          return errors.some(error =>
            error.includes('required') ||
            error.includes('invalid format') ||
            error.includes('not a valid choice')
          );
        });

        if (section === 'basic_info' && hasCriticalErrors) {
          toast.dismiss(loadingToastId);
          toast.error(`Please fix critical validation errors in ${section} before saving`, {
            duration: 4000,
            icon: <AlertCircle className="w-4 h-4" />
          });
          return;
        }

        // Transform the data to match backend schema
        // Use fullSectionData instead of sectionChanges to ensure complete data transformation
        const transformedData = transformPreferenceData({
          [section]: fullSectionData
        });

        console.log('🔄 Saving section:', section, 'with data:', transformedData);

        // Debug: Log the exact payload being sent to the API
        console.log('📤 API Payload Details:', {
          section: section,
          originalSectionChanges: sectionChanges,
          fullSectionData: fullSectionData,
          transformedData: transformedData,
          apiEndpoint: '/api/preferences/',
          method: 'PATCH',
          dataSource: 'fullSectionData (merged with existing preferences)'
        });

        // Save this section
        await updatePreferencesWithRetry(transformedData, dispatch, 3);
      }

      // Clear local changes after successful save
      setLocalChanges({});
      setIsDirty(false);
      setLastSaved(new Date());
      setHasChanges(false);

      toast.dismiss(loadingToastId);
      toast.success('All preferences saved successfully!', {
        duration: 3000,
        icon: <CheckCircle className="w-4 h-4" />
      });

      // Log the preference save interaction
      const validationSummary = validation.summary;
      logUserInteraction(dispatch, 'page_view', {
        sections_saved: Object.keys(localChanges),
        validation_state: validation.isValid,
        completion_percentage: validationSummary?.completionPercentage || 0,
        timestamp: new Date().toISOString()
      }, {
        page: 'preferences_dashboard',
        action: 'manual_preferences_save'
      });

    } catch (error) {
      toast.dismiss(loadingToastId);

      // Enhanced error logging for debugging
      console.error('❌ Failed to save preferences - Full error details:', {
        error,
        errorData: error?.data,
        errorMessage: error?.message,
        errorStatus: error?.status,
        errorResponse: error?.response,
        localChanges: localChanges,
        stack: error?.stack
      });

      // Extract detailed error information
      let detailedError = 'Failed to save preferences. Please try again.';

      if (error?.data) {
        // RTK Query error with data
        if (typeof error.data === 'string') {
          detailedError = error.data;
        } else if (error.data.message) {
          detailedError = error.data.message;
        } else if (error.data.detail) {
          detailedError = error.data.detail;
        } else {
          detailedError = JSON.stringify(error.data);
        }
      } else if (error?.message) {
        detailedError = error.message;
      }

      const errorMessage = error?.attempts > 1
        ? `Failed to save preferences after ${error.attempts} attempts. ${detailedError}`
        : detailedError;

      toast.error(errorMessage, {
        duration: 8000,  // Longer duration for debugging
        icon: <AlertCircle className="w-4 h-4" />
      });
    }
  };

  // Get merged preferences (saved + local changes)
  const getMergedPreferences = () => {
    if (!userPreferences) return null;

    const merged = { ...userPreferences };

    // Apply local changes
    Object.keys(localChanges).forEach(section => {
      merged[section] = {
        ...merged[section],
        ...localChanges[section]
      };
    });

    return merged;
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
        window.location.href = '/app/onboarding';
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

                {/* Unsaved changes indicator */}
                {isDirty && (
                  <div className="flex items-center space-x-2 text-amber-600">
                    <AlertCircle className="h-4 w-4" />
                    <span className="text-sm font-medium">
                      {Object.keys(localChanges).length} unsaved change{Object.keys(localChanges).length !== 1 ? 's' : ''}
                    </span>
                  </div>
                )}

                {/* Save Changes button - only show when there are unsaved changes */}
                {isDirty && (
                  <Button
                    onClick={handleSaveChanges}
                    disabled={saving}
                    className="bg-green-600 hover:bg-green-700 text-white"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </Button>
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
                    onClick={() => window.location.href = '/app/onboarding'}
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
                  preferences={getMergedPreferences()}
                  loading={loading}
                  validation={validation}
                  onPreferenceChange={handleLocalPreferenceChange}
                  onResetToOnboarding={resetToOnboarding}
                  isDirty={isDirty}
                  localChanges={localChanges}
                />
              </TabsContent>

              <TabsContent value="goals" className="space-y-6">
                <LearningGoalsManager
                  preferences={getMergedPreferences()}
                  loading={loading}
                  validation={validation}
                  onPreferenceChange={handleLocalPreferenceChange}
                  isDirty={isDirty}
                  localChanges={localChanges}
                />
              </TabsContent>

              <TabsContent value="content" className="space-y-6">
                <ContentPreferences
                  preferences={getMergedPreferences()}
                  loading={loading}
                  validation={validation}
                  onPreferenceChange={handleLocalPreferenceChange}
                  isDirty={isDirty}
                  localChanges={localChanges}
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
                  preferences={getMergedPreferences()}
                  recommendations={recommendationsData}
                  loading={loading || recommendationsLoading}
                  onPreferenceChange={handleLocalPreferenceChange}
                  onRefreshRecommendations={refetchRecommendations}
                  isDirty={isDirty}
                  localChanges={localChanges}
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