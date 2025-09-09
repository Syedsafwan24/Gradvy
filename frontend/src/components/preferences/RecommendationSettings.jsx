'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  Star, 
  RefreshCw,
  Settings,
  Target,
  Sparkles,
  Eye,
  ThumbsUp,
  ThumbsDown,
  BookOpen,
  Clock,
  DollarSign,
  Users,
  AlertCircle,
  CheckCircle,
  Filter
} from 'lucide-react';

export default function RecommendationSettings({ preferences, loading, onPreferenceChange }) {
  const [recommendations, setRecommendations] = useState([]);
  const [loadingRecommendations, setLoadingRecommendations] = useState(true);
  const [generatingRecommendations, setGeneratingRecommendations] = useState(false);
  
  // Recommendation settings
  const [enablePersonalization, setEnablePersonalization] = useState(true);
  const [diversityLevel, setDiversityLevel] = useState([75]);
  const [maxRecommendations, setMaxRecommendations] = useState([10]);
  const [includePopularCourses, setIncludePopularCourses] = useState(true);
  const [includeFreeContent, setIncludeFreeContent] = useState(true);
  const [considerRatings, setConsiderRatings] = useState(true);
  const [adaptiveLearning, setAdaptiveLearning] = useState(true);

  useEffect(() => {
    if (preferences) {
      loadRecommendations();
    }
  }, [preferences]);

  const loadRecommendations = async () => {
    setLoadingRecommendations(true);
    try {
      const response = await fetch('/api/preferences/recommendations/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations || []);
      }
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoadingRecommendations(false);
    }
  };

  const generateNewRecommendations = async () => {
    setGeneratingRecommendations(true);
    try {
      const response = await fetch('/api/preferences/recommendations/generate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: JSON.stringify({
          personalization_enabled: enablePersonalization,
          diversity_level: diversityLevel[0] / 100,
          max_recommendations: maxRecommendations[0],
          include_popular: includePopularCourses,
          include_free: includeFreeContent,
          consider_ratings: considerRatings,
          adaptive_learning: adaptiveLearning
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations || []);
      }
    } catch (error) {
      console.error('Failed to generate recommendations:', error);
    } finally {
      setGeneratingRecommendations(false);
    }
  };

  const provideFeedback = async (recommendationId, feedback) => {
    try {
      await fetch('/api/preferences/recommendations/feedback/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: JSON.stringify({
          recommendation_id: recommendationId,
          feedback,
          timestamp: new Date().toISOString()
        }),
      });
      
      // Update local state to reflect feedback
      setRecommendations(prev => 
        prev.map(rec => 
          rec.course_id === recommendationId 
            ? { ...rec, user_feedback: feedback }
            : rec
        )
      );
    } catch (error) {
      console.error('Failed to provide feedback:', error);
    }
  };

  const getPlatformIcon = (platform) => {
    const icons = {
      'udemy': '🎓',
      'coursera': '🏛️',
      'youtube': '📺',
      'edx': '🎯',
      'pluralsight': '💡',
      'linkedin_learning': '💼',
      'codecademy': '👨‍💻',
      'freecodecamp': '🔥'
    };
    return icons[platform] || '📚';
  };

  const formatPrice = (metadata) => {
    if (metadata?.price === 0 || metadata?.free) return 'Free';
    if (metadata?.price) return `$${metadata.price}`;
    return 'Price varies';
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

  if (loading) {
    return (
      <div className="space-y-6">
        {[1, 2].map((i) => (
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

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Recommendation Settings */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Settings className="h-5 w-5 text-blue-600" />
              <span>Recommendation Settings</span>
            </CardTitle>
            <p className="text-sm text-gray-600">
              Customize how course recommendations are generated for you
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Basic Settings */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">Personalization</h4>
                    <p className="text-sm text-gray-600">Use your learning history for recommendations</p>
                  </div>
                  <Switch
                    checked={enablePersonalization}
                    onCheckedChange={setEnablePersonalization}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">Include Popular Courses</h4>
                    <p className="text-sm text-gray-600">Show trending and highly-rated courses</p>
                  </div>
                  <Switch
                    checked={includePopularCourses}
                    onCheckedChange={setIncludePopularCourses}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">Include Free Content</h4>
                    <p className="text-sm text-gray-600">Show free courses and materials</p>
                  </div>
                  <Switch
                    checked={includeFreeContent}
                    onCheckedChange={setIncludeFreeContent}
                  />
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">Consider Ratings</h4>
                    <p className="text-sm text-gray-600">Prioritize highly-rated courses</p>
                  </div>
                  <Switch
                    checked={considerRatings}
                    onCheckedChange={setConsiderRatings}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">Adaptive Learning</h4>
                    <p className="text-sm text-gray-600">Adjust recommendations based on progress</p>
                  </div>
                  <Switch
                    checked={adaptiveLearning}
                    onCheckedChange={setAdaptiveLearning}
                  />
                </div>
              </div>
            </div>

            {/* Advanced Settings */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Content Diversity Level
                </label>
                <div className="space-y-2">
                  <Slider
                    value={diversityLevel}
                    onValueChange={setDiversityLevel}
                    min={0}
                    max={100}
                    step={5}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>Similar content</span>
                    <span className="font-medium">{diversityLevel[0]}%</span>
                    <span>Diverse content</span>
                  </div>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Maximum Recommendations
                </label>
                <div className="space-y-2">
                  <Slider
                    value={maxRecommendations}
                    onValueChange={setMaxRecommendations}
                    min={5}
                    max={25}
                    step={1}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>5 courses</span>
                    <span className="font-medium">{maxRecommendations[0]} courses</span>
                    <span>25 courses</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex space-x-3">
              <Button
                onClick={generateNewRecommendations}
                disabled={generatingRecommendations}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {generatingRecommendations ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Generate New Recommendations
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Current Recommendations */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-purple-600" />
                <span>Your Recommendations</span>
                {recommendations.length > 0 && (
                  <Badge variant="secondary">{recommendations.length} courses</Badge>
                )}
              </CardTitle>
              
              {!loadingRecommendations && recommendations.length > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadRecommendations}
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {loadingRecommendations ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse">
                    <div className="flex space-x-4">
                      <div className="w-16 h-16 bg-gray-200 rounded-lg"></div>
                      <div className="flex-1 space-y-2">
                        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : recommendations.length === 0 ? (
              <div className="text-center py-8">
                <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Recommendations Yet</h3>
                <p className="text-gray-600 mb-4">
                  Complete your preferences to get personalized course recommendations.
                </p>
                <Button onClick={generateNewRecommendations} className="bg-blue-600 hover:bg-blue-700">
                  <Sparkles className="h-4 w-4 mr-2" />
                  Generate Recommendations
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {recommendations.map((recommendation, index) => (
                  <motion.div
                    key={recommendation.course_id || index}
                    variants={itemVariants}
                    className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                  >
                    <div className="flex space-x-4">
                      <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-2xl">
                        {getPlatformIcon(recommendation.platform)}
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900 mb-1">
                              {recommendation.title}
                            </h4>
                            <div className="flex items-center space-x-2 mb-2">
                              <Badge variant="outline" className="text-xs capitalize">
                                {recommendation.platform}
                              </Badge>
                              
                              {recommendation.metadata?.rating && (
                                <div className="flex items-center space-x-1">
                                  <Star className="h-3 w-3 text-yellow-500 fill-current" />
                                  <span className="text-sm">{recommendation.metadata.rating.toFixed(1)}</span>
                                </div>
                              )}
                              
                              {recommendation.metadata?.students && (
                                <div className="flex items-center space-x-1">
                                  <Users className="h-3 w-3 text-gray-500" />
                                  <span className="text-sm text-gray-600">
                                    {recommendation.metadata.students.toLocaleString()}
                                  </span>
                                </div>
                              )}
                            </div>
                            
                            {recommendation.reasoning && recommendation.reasoning.length > 0 && (
                              <div className="flex flex-wrap gap-1 mb-2">
                                {recommendation.reasoning.slice(0, 3).map((reason, idx) => (
                                  <Badge key={idx} variant="secondary" className="text-xs">
                                    {reason.replace('_', ' ')}
                                  </Badge>
                                ))}
                              </div>
                            )}
                            
                            <div className="flex items-center space-x-4 text-sm text-gray-600">
                              {recommendation.metadata?.duration && (
                                <div className="flex items-center space-x-1">
                                  <Clock className="h-3 w-3" />
                                  <span>{recommendation.metadata.duration}</span>
                                </div>
                              )}
                              
                              <div className="flex items-center space-x-1">
                                <DollarSign className="h-3 w-3" />
                                <span>{formatPrice(recommendation.metadata)}</span>
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <div className="text-center">
                              <div className="text-lg font-bold text-blue-600">
                                {Math.round(recommendation.score * 100)}%
                              </div>
                              <div className="text-xs text-gray-500">Match</div>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between mt-3">
                          <div className="flex items-center space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => window.open(recommendation.url || '#', '_blank')}
                            >
                              <Eye className="h-4 w-4 mr-1" />
                              View Course
                            </Button>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <Button
                              variant={recommendation.user_feedback === 'positive' ? 'default' : 'ghost'}
                              size="sm"
                              onClick={() => provideFeedback(recommendation.course_id, 'positive')}
                            >
                              <ThumbsUp className="h-4 w-4" />
                            </Button>
                            <Button
                              variant={recommendation.user_feedback === 'negative' ? 'default' : 'ghost'}
                              size="sm"
                              onClick={() => provideFeedback(recommendation.course_id, 'negative')}
                            >
                              <ThumbsDown className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Recommendation Tips */}
      <motion.div variants={itemVariants}>
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="p-4">
            <div className="flex items-start space-x-3">
              <Sparkles className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-900">Improve Your Recommendations</h4>
                <div className="text-sm text-blue-700 mt-1 space-y-1">
                  <p>• Provide feedback on recommended courses to improve accuracy</p>
                  <p>• Keep your learning goals and preferences up to date</p>
                  <p>• Use the learning platform to track your progress</p>
                  <p>• Try different diversity levels to explore new topics</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}