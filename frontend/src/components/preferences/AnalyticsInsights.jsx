'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  BarChart3, 
  TrendingUp, 
  Brain,
  Target,
  Clock,
  Star,
  Award,
  Activity,
  Eye,
  Lightbulb,
  Calendar,
  BookOpen,
  Users,
  Zap,
  RefreshCw,
  Download,
  AlertCircle
} from 'lucide-react';

export default function AnalyticsInsights({ preferences, loading }) {
  const [insights, setInsights] = useState(null);
  const [learningPatterns, setLearningPatterns] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loadingInsights, setLoadingInsights] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (preferences) {
      loadAnalyticsData();
    }
  }, [preferences]);

  const loadAnalyticsData = async () => {
    setLoadingInsights(true);
    try {
      // Load AI insights
      const insightsResponse = await fetch('/api/preferences/ai-insights/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });

      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setInsights(insightsData);
      }

      // Load learning patterns
      const patternsResponse = await fetch('/api/preferences/learning-patterns/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });

      if (patternsResponse.ok) {
        const patternsData = await patternsResponse.json();
        setLearningPatterns(patternsData);
      }

      // Load analytics-based recommendations
      const recResponse = await fetch('/api/preferences/recommendations/?type=analytics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });

      if (recResponse.ok) {
        const recData = await recResponse.json();
        setRecommendations(recData.recommendations || []);
      }
    } catch (error) {
      console.error('Failed to load analytics data:', error);
    } finally {
      setLoadingInsights(false);
    }
  };

  const refreshInsights = async () => {
    setRefreshing(true);
    try {
      const response = await fetch('/api/preferences/ai-insights/refresh/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });

      if (response.ok) {
        await loadAnalyticsData();
      }
    } catch (error) {
      console.error('Failed to refresh insights:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const getInsightIcon = (type) => {
    switch (type) {
      case 'strength': return { icon: Star, color: 'text-yellow-600', bg: 'bg-yellow-100' };
      case 'improvement': return { icon: TrendingUp, color: 'text-blue-600', bg: 'bg-blue-100' };
      case 'pattern': return { icon: Brain, color: 'text-purple-600', bg: 'bg-purple-100' };
      case 'recommendation': return { icon: Lightbulb, color: 'text-green-600', bg: 'bg-green-100' };
      default: return { icon: Eye, color: 'text-gray-600', bg: 'bg-gray-100' };
    }
  };

  const formatLearningTime = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    
    if (hours > 0) {
      return `${hours}h ${remainingMinutes}m`;
    }
    return `${minutes}m`;
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

  if (loading || loadingInsights) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="h-20 bg-gray-200 rounded"></div>
                <div className="h-3 bg-gray-200 rounded w-3/4"></div>
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
      {/* AI Insights Overview */}
      <motion.div variants={itemVariants}>
        <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <Brain className="h-5 w-5 text-purple-600" />
                <span>AI Learning Insights</span>
                {insights?.updated_at && (
                  <Badge variant="outline" className="text-xs">
                    Updated {new Date(insights.updated_at).toLocaleDateString()}
                  </Badge>
                )}
              </CardTitle>
              
              <Button
                variant="outline"
                size="sm"
                onClick={refreshInsights}
                disabled={refreshing}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
            <p className="text-sm text-gray-600">
              AI-powered insights based on your learning behavior and preferences
            </p>
          </CardHeader>
          <CardContent>
            {!insights || (!insights.strength_areas?.length && !insights.improvement_areas?.length) ? (
              <div className="text-center py-8">
                <AlertCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500 mb-4">
                  Not enough data for AI insights yet. Keep learning to see personalized insights!
                </p>
                <Button onClick={refreshInsights} variant="outline">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Check for Insights
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Strengths */}
                {insights.strength_areas?.length > 0 && (
                  <div>
                    <h4 className="font-medium text-green-900 mb-3 flex items-center">
                      <Star className="h-4 w-4 mr-2 text-green-600" />
                      Your Learning Strengths
                    </h4>
                    <div className="grid md:grid-cols-2 gap-3">
                      {insights.strength_areas.map((strength, index) => (
                        <div key={index} className="p-3 bg-green-50 rounded-lg border border-green-200">
                          <p className="text-sm text-green-800 font-medium">{strength}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Improvement Areas */}
                {insights.improvement_areas?.length > 0 && (
                  <div>
                    <h4 className="font-medium text-blue-900 mb-3 flex items-center">
                      <TrendingUp className="h-4 w-4 mr-2 text-blue-600" />
                      Areas for Growth
                    </h4>
                    <div className="grid md:grid-cols-2 gap-3">
                      {insights.improvement_areas.map((area, index) => (
                        <div key={index} className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                          <p className="text-sm text-blue-800 font-medium">{area}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recommended Paths */}
                {insights.recommended_paths?.length > 0 && (
                  <div>
                    <h4 className="font-medium text-purple-900 mb-3 flex items-center">
                      <Target className="h-4 w-4 mr-2 text-purple-600" />
                      Recommended Learning Paths
                    </h4>
                    <div className="space-y-3">
                      {insights.recommended_paths.slice(0, 3).map((path, index) => (
                        <div key={index} className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                          <h5 className="font-medium text-purple-900 mb-1">{path.title}</h5>
                          <p className="text-sm text-purple-700 mb-2">{path.description}</p>
                          <div className="flex items-center space-x-4 text-xs text-purple-600">
                            <span>Duration: {path.duration}</span>
                            <span>Difficulty: {path.difficulty}</span>
                            {path.priority && (
                              <Badge variant="outline" className="text-xs">
                                {path.priority} priority
                              </Badge>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Learning Patterns */}
      {learningPatterns && (
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-orange-600" />
                <span>Learning Patterns</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Peak Learning Time */}
                {learningPatterns.peak_hours && (
                  <div className="text-center">
                    <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                      <Clock className="h-6 w-6 text-orange-600" />
                    </div>
                    <h4 className="font-medium text-gray-900">Peak Learning Time</h4>
                    <p className="text-2xl font-bold text-orange-600">{learningPatterns.peak_hours}</p>
                    <p className="text-sm text-gray-600">Most active hours</p>
                  </div>
                )}

                {/* Average Session */}
                {learningPatterns.avg_session_duration && (
                  <div className="text-center">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                      <Zap className="h-6 w-6 text-blue-600" />
                    </div>
                    <h4 className="font-medium text-gray-900">Average Session</h4>
                    <p className="text-2xl font-bold text-blue-600">
                      {formatLearningTime(learningPatterns.avg_session_duration)}
                    </p>
                    <p className="text-sm text-gray-600">Session length</p>
                  </div>
                )}

                {/* Completion Rate */}
                {learningPatterns.completion_rate && (
                  <div className="text-center">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                      <Award className="h-6 w-6 text-green-600" />
                    </div>
                    <h4 className="font-medium text-gray-900">Completion Rate</h4>
                    <p className="text-2xl font-bold text-green-600">
                      {Math.round(learningPatterns.completion_rate)}%
                    </p>
                    <p className="text-sm text-gray-600">Course completion</p>
                  </div>
                )}

                {/* Preferred Content */}
                {learningPatterns.preferred_content_type && (
                  <div className="text-center">
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                      <BookOpen className="h-6 w-6 text-purple-600" />
                    </div>
                    <h4 className="font-medium text-gray-900">Preferred Content</h4>
                    <p className="text-lg font-bold text-purple-600 capitalize">
                      {learningPatterns.preferred_content_type.replace('_', ' ')}
                    </p>
                    <p className="text-sm text-gray-600">Most engaged with</p>
                  </div>
                )}

                {/* Learning Streak */}
                {learningPatterns.current_streak && (
                  <div className="text-center">
                    <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                      <TrendingUp className="h-6 w-6 text-red-600" />
                    </div>
                    <h4 className="font-medium text-gray-900">Current Streak</h4>
                    <p className="text-2xl font-bold text-red-600">
                      {learningPatterns.current_streak} days
                    </p>
                    <p className="text-sm text-gray-600">Consecutive learning</p>
                  </div>
                )}

                {/* Total Learning Time */}
                {learningPatterns.total_learning_time && (
                  <div className="text-center">
                    <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                      <Calendar className="h-6 w-6 text-yellow-600" />
                    </div>
                    <h4 className="font-medium text-gray-900">Total Learning Time</h4>
                    <p className="text-2xl font-bold text-yellow-600">
                      {formatLearningTime(learningPatterns.total_learning_time)}
                    </p>
                    <p className="text-sm text-gray-600">All time</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Analytics-Based Recommendations */}
      {recommendations.length > 0 && (
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Lightbulb className="h-5 w-5 text-yellow-600" />
                <span>Smart Recommendations</span>
                <Badge variant="secondary">Based on Analytics</Badge>
              </CardTitle>
              <p className="text-sm text-gray-600">
                Courses recommended based on your learning patterns and performance
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recommendations.slice(0, 5).map((rec, index) => (
                  <div key={index} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-1">{rec.title}</h4>
                        <p className="text-sm text-gray-600 mb-2">{rec.description}</p>
                        
                        <div className="flex items-center space-x-4 text-sm">
                          <Badge variant="outline" className="text-xs">
                            {rec.platform}
                          </Badge>
                          
                          {rec.analytics_reason && (
                            <span className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                              {rec.analytics_reason}
                            </span>
                          )}
                          
                          {rec.difficulty && (
                            <span className="text-xs text-gray-500">
                              {rec.difficulty} level
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="text-center">
                        <div className="text-lg font-bold text-green-600">
                          {Math.round(rec.score * 100)}%
                        </div>
                        <div className="text-xs text-gray-500">Match</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Performance Metrics */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-indigo-600" />
              <span>Performance Metrics</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Learning Goals Progress */}
              {preferences?.basic_info?.learning_goals && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Learning Goals Progress</h4>
                  <div className="space-y-3">
                    {preferences.basic_info.learning_goals.slice(0, 5).map((goal, index) => {
                      // Mock progress data - in real app, this would come from analytics
                      const progress = Math.random() * 100;
                      const status = progress > 70 ? 'text-green-600' : progress > 40 ? 'text-yellow-600' : 'text-red-600';
                      
                      return (
                        <div key={index} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium capitalize">
                              {goal.replace('_', ' ')}
                            </span>
                            <span className={`text-sm ${status}`}>
                              {Math.round(progress)}%
                            </span>
                          </div>
                          <Progress value={progress} className="h-2" />
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Export Analytics */}
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Export Analytics Data</h4>
                  <p className="text-sm text-gray-600">
                    Download your learning analytics and insights
                  </p>
                </div>
                <Button variant="outline" onClick={() => {
                  // TODO: Implement analytics export
                  console.log('Exporting analytics data...');
                }}>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}