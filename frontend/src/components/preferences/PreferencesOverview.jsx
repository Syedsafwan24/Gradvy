'use client';

import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Target, 
  Clock, 
  BookOpen, 
  TrendingUp, 
  User, 
  Calendar,
  Globe,
  Award,
  RotateCcw,
  Edit,
  AlertCircle,
  CheckCircle,
  Settings
} from 'lucide-react';

export default function PreferencesOverview({ preferences, loading, onPreferenceChange, onResetToOnboarding }) {
  if (loading) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!preferences) {
    return (
      <Card className="text-center p-8">
        <CardContent>
          <AlertCircle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No Preferences Found</h3>
          <p className="text-gray-600 mb-6">
            It looks like you haven't completed your learning preferences yet. 
            Complete the onboarding process to get personalized recommendations.
          </p>
          <Button 
            onClick={() => window.location.href = '/onboarding'}
            className="bg-blue-600 hover:bg-blue-700"
          >
            Complete Onboarding
          </Button>
        </CardContent>
      </Card>
    );
  }

  const basicInfo = preferences.basic_info || {};
  const contentPrefs = preferences.content_preferences || {};
  const createdDate = preferences.created_at ? new Date(preferences.created_at).toLocaleDateString() : 'Unknown';
  const updatedDate = preferences.updated_at ? new Date(preferences.updated_at).toLocaleDateString() : 'Unknown';

  // Calculate completion percentage
  const calculateCompletionScore = () => {
    let score = 0;
    const maxScore = 8;

    if (basicInfo.learning_goals?.length > 0) score += 1;
    if (basicInfo.experience_level) score += 1;
    if (basicInfo.preferred_pace) score += 1;
    if (basicInfo.time_availability) score += 1;
    if (basicInfo.learning_style?.length > 0) score += 1;
    if (basicInfo.career_stage) score += 1;
    if (contentPrefs.preferred_platforms?.length > 0) score += 1;
    if (contentPrefs.content_types?.length > 0) score += 1;

    return Math.round((score / maxScore) * 100);
  };

  const completionScore = calculateCompletionScore();

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
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Profile Summary */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <User className="h-5 w-5 text-blue-600" />
              <span>Profile Summary</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Profile Completion</h4>
                  <div className="flex items-center space-x-3">
                    <Progress value={completionScore} className="flex-1" />
                    <span className="text-sm font-medium">{completionScore}%</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {completionScore === 100 ? 'Complete profile' : 'Complete your profile for better recommendations'}
                  </p>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Account Information</h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Created:</span>
                      <span>{createdDate}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Last Updated:</span>
                      <span>{updatedDate}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Quick Actions</h4>
                  <div className="space-y-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.location.href = '/onboarding'}
                      className="w-full justify-start"
                    >
                      <Edit className="h-4 w-4 mr-2" />
                      Re-take Onboarding
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={onResetToOnboarding}
                      className="w-full justify-start text-red-600 hover:text-red-700"
                    >
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Reset All Preferences
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Learning Profile */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-green-600" />
              <span>Learning Profile</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Learning Goals */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                  <Target className="h-4 w-4 mr-1 text-blue-500" />
                  Goals
                </h4>
                <div className="space-y-1">
                  {basicInfo.learning_goals?.length > 0 ? (
                    <>
                      {basicInfo.learning_goals.slice(0, 3).map((goal, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {goal.replace('_', ' ')}
                        </Badge>
                      ))}
                      {basicInfo.learning_goals.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{basicInfo.learning_goals.length - 3} more
                        </Badge>
                      )}
                    </>
                  ) : (
                    <p className="text-sm text-gray-500">Not set</p>
                  )}
                </div>
              </div>

              {/* Experience Level */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                  <Award className="h-4 w-4 mr-1 text-purple-500" />
                  Experience
                </h4>
                <p className="text-sm capitalize">
                  {basicInfo.experience_level?.replace('_', ' ') || 'Not set'}
                </p>
                <p className="text-xs text-gray-500">Current level</p>
              </div>

              {/* Learning Pace */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                  <TrendingUp className="h-4 w-4 mr-1 text-orange-500" />
                  Pace
                </h4>
                <p className="text-sm capitalize">
                  {basicInfo.preferred_pace || 'Not set'}
                </p>
                <p className="text-xs text-gray-500">Learning speed</p>
              </div>

              {/* Time Availability */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                  <Clock className="h-4 w-4 mr-1 text-green-500" />
                  Time
                </h4>
                <p className="text-sm">
                  {basicInfo.time_availability || 'Not set'}
                </p>
                <p className="text-xs text-gray-500">Per week</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Learning Preferences */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Settings className="h-5 w-5 text-purple-600" />
              <span>Learning Preferences</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              {/* Learning Styles */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Learning Styles</h4>
                <div className="flex flex-wrap gap-1">
                  {basicInfo.learning_style?.length > 0 ? (
                    basicInfo.learning_style.map((style, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {style.replace('_', ' ')}
                      </Badge>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500">Not specified</p>
                  )}
                </div>
              </div>

              {/* Career & Timeline */}
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-gray-900 mb-1">Career Stage</h4>
                  <p className="text-sm capitalize">
                    {basicInfo.career_stage?.replace('_', ' ') || 'Not specified'}
                  </p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-1">Target Timeline</h4>
                  <p className="text-sm">
                    {basicInfo.target_timeline || 'Not specified'}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Content Preferences */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BookOpen className="h-5 w-5 text-indigo-600" />
              <span>Content Preferences</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              {/* Platforms */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Preferred Platforms</h4>
                <div className="flex flex-wrap gap-1">
                  {contentPrefs.preferred_platforms?.length > 0 ? (
                    contentPrefs.preferred_platforms.map((platform, index) => (
                      <Badge key={index} variant="secondary" className="text-xs capitalize">
                        {platform.replace('_', ' ')}
                      </Badge>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500">Not specified</p>
                  )}
                </div>
              </div>

              {/* Content Types */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Content Types</h4>
                <div className="flex flex-wrap gap-1">
                  {contentPrefs.content_types?.length > 0 ? (
                    contentPrefs.content_types.map((type, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {type}
                      </Badge>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500">Not specified</p>
                  )}
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-4 mt-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-1">Difficulty</h4>
                <p className="text-sm capitalize">
                  {contentPrefs.difficulty_preference || 'Mixed'}
                </p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-1">Duration</h4>
                <p className="text-sm capitalize">
                  {contentPrefs.duration_preference || 'Mixed'}
                </p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-1">Languages</h4>
                <div className="flex flex-wrap gap-1">
                  {contentPrefs.language_preference?.map((lang, index) => (
                    <Badge key={index} variant="outline" className="text-xs capitalize">
                      {lang}
                    </Badge>
                  )) || <p className="text-sm">English</p>}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Completion Status */}
      {completionScore < 100 && (
        <motion.div variants={itemVariants}>
          <Card className="border-yellow-200 bg-yellow-50">
            <CardContent className="p-4">
              <div className="flex items-start space-x-3">
                <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-medium text-yellow-800">Improve Your Recommendations</h4>
                  <p className="text-sm text-yellow-700 mt-1">
                    Complete your profile to get more accurate course recommendations. 
                    Missing information may result in less relevant suggestions.
                  </p>
                  <Button 
                    size="sm" 
                    className="mt-3 bg-yellow-600 hover:bg-yellow-700"
                    onClick={() => window.location.href = '/onboarding'}
                  >
                    Complete Profile
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </motion.div>
  );
}