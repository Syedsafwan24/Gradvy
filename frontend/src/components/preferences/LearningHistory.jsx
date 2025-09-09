'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Clock, 
  Play, 
  BookOpen, 
  TrendingUp,
  Calendar,
  Activity,
  Award,
  Target,
  BarChart3,
  Download,
  Filter,
  Search,
  Eye,
  ChevronRight,
  AlertCircle
} from 'lucide-react';

export default function LearningHistory({ preferences, loading }) {
  const [sessions, setSessions] = useState([]);
  const [interactions, setInteractions] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [activeTab, setActiveTab] = useState('sessions');
  const [timeFilter, setTimeFilter] = useState('30d');

  useEffect(() => {
    if (preferences) {
      loadLearningHistory();
      loadAnalytics();
    }
  }, [preferences, timeFilter]);

  const loadLearningHistory = async () => {
    setLoadingHistory(true);
    try {
      // Load learning sessions
      const sessionsResponse = await fetch(`/api/preferences/learning-sessions/?timeframe=${timeFilter}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });

      if (sessionsResponse.ok) {
        const sessionsData = await sessionsResponse.json();
        setSessions(sessionsData.results || []);
      }

      // Load interactions
      const interactionsResponse = await fetch(`/api/preferences/interactions/?timeframe=${timeFilter}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });

      if (interactionsResponse.ok) {
        const interactionsData = await interactionsResponse.json();
        setInteractions(interactionsData.results || []);
      }
    } catch (error) {
      console.error('Failed to load learning history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await fetch(`/api/preferences/analytics/?timeframe=${timeFilter}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Failed to load analytics:', error);
    }
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getInteractionIcon = (type) => {
    switch (type) {
      case 'course_click': return '👆';
      case 'video_watch': return '📺';
      case 'quiz_attempt': return '📝';
      case 'search': return '🔍';
      case 'bookmark': return '🔖';
      case 'course_enroll': return '📚';
      case 'course_complete': return '🎓';
      case 'rating_given': return '⭐';
      default: return '📊';
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

  if (loading || loadingHistory) {
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

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Analytics Overview */}
      {analytics && (
        <motion.div variants={itemVariants}>
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5 text-blue-600" />
                <span>Learning Analytics</span>
                <Badge variant="secondary" className="ml-2">
                  Last {timeFilter === '7d' ? '7 days' : timeFilter === '30d' ? '30 days' : '90 days'}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {analytics.total_sessions || 0}
                  </div>
                  <p className="text-sm text-gray-600">Learning Sessions</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {formatDuration(analytics.total_time || 0)}
                  </div>
                  <p className="text-sm text-gray-600">Total Time</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {analytics.courses_viewed || 0}
                  </div>
                  <p className="text-sm text-gray-600">Courses Viewed</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {Math.round(analytics.avg_session_duration / 60) || 0}m
                  </div>
                  <p className="text-sm text-gray-600">Avg Session</p>
                </div>
              </div>
              
              {analytics.streak_days > 0 && (
                <div className="mt-4 p-3 bg-orange-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Award className="h-5 w-5 text-orange-500" />
                    <span className="font-medium text-orange-800">
                      {analytics.streak_days} day learning streak! 🔥
                    </span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Time Filter */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <Clock className="h-5 w-5 text-green-600" />
                <span>Learning History</span>
              </CardTitle>
              <div className="flex items-center space-x-2">
                <Button
                  variant={timeFilter === '7d' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTimeFilter('7d')}
                >
                  7 Days
                </Button>
                <Button
                  variant={timeFilter === '30d' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTimeFilter('30d')}
                >
                  30 Days
                </Button>
                <Button
                  variant={timeFilter === '90d' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTimeFilter('90d')}
                >
                  90 Days
                </Button>
              </div>
            </div>
          </CardHeader>
          
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
              <TabsList className="grid grid-cols-2">
                <TabsTrigger value="sessions" className="flex items-center space-x-2">
                  <Play className="h-4 w-4" />
                  <span>Learning Sessions</span>
                </TabsTrigger>
                <TabsTrigger value="interactions" className="flex items-center space-x-2">
                  <Activity className="h-4 w-4" />
                  <span>Interactions</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="sessions" className="space-y-4">
                {sessions.length === 0 ? (
                  <div className="text-center py-8">
                    <AlertCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500">No learning sessions found for this period.</p>
                    <p className="text-sm text-gray-400 mt-1">
                      Start learning to see your progress here!
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {sessions.map((session, index) => (
                      <motion.div
                        key={session.session_id || index}
                        variants={itemVariants}
                        className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                              <Play className="h-5 w-5 text-blue-600" />
                            </div>
                            <div>
                              <h4 className="font-medium text-gray-900">
                                Learning Session
                              </h4>
                              <p className="text-sm text-gray-600">
                                {formatDate(session.start_time)}
                              </p>
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-4">
                            <div className="text-right">
                              <p className="text-sm font-medium">
                                {formatDuration(session.duration || 0)}
                              </p>
                              <p className="text-xs text-gray-500">
                                {session.activities?.length || 0} activities
                              </p>
                            </div>
                            
                            {session.device_info && (
                              <Badge variant="outline" className="text-xs">
                                {session.device_info.type}
                              </Badge>
                            )}
                          </div>
                        </div>
                        
                        {session.activities && session.activities.length > 0 && (
                          <div className="mt-3 space-y-2">
                            <h5 className="text-sm font-medium text-gray-700">Activities:</h5>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                              {session.activities.slice(0, 4).map((activity, actIndex) => (
                                <div key={actIndex} className="flex items-center space-x-2 text-sm">
                                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                  <span className="capitalize">{activity.activity_type?.replace('_', ' ')}</span>
                                  <span className="text-gray-500">
                                    ({formatDuration(activity.duration || 0)})
                                  </span>
                                  {activity.completion_rate && (
                                    <Progress 
                                      value={activity.completion_rate * 100} 
                                      className="w-16 h-1"
                                    />
                                  )}
                                </div>
                              ))}
                              {session.activities.length > 4 && (
                                <div className="text-sm text-gray-500">
                                  +{session.activities.length - 4} more activities
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </div>
                )}
              </TabsContent>

              <TabsContent value="interactions" className="space-y-4">
                {interactions.length === 0 ? (
                  <div className="text-center py-8">
                    <AlertCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500">No interactions found for this period.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {interactions.map((interaction, index) => (
                      <motion.div
                        key={interaction.id || index}
                        variants={itemVariants}
                        className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="text-2xl">
                              {getInteractionIcon(interaction.type)}
                            </div>
                            <div>
                              <h4 className="font-medium text-gray-900 capitalize">
                                {interaction.type?.replace('_', ' ')}
                              </h4>
                              <p className="text-sm text-gray-600">
                                {formatDate(interaction.timestamp)}
                              </p>
                            </div>
                          </div>
                          
                          <div className="text-right">
                            {interaction.data?.course_id && (
                              <p className="text-sm text-gray-600">
                                Course: {interaction.data.course_id}
                              </p>
                            )}
                            {interaction.data?.duration && (
                              <p className="text-xs text-gray-500">
                                {formatDuration(interaction.data.duration)}
                              </p>
                            )}
                            {interaction.data?.rating && (
                              <div className="flex items-center space-x-1">
                                <span className="text-xs">Rating:</span>
                                <div className="flex">
                                  {[...Array(5)].map((_, i) => (
                                    <span 
                                      key={i} 
                                      className={`text-xs ${i < interaction.data.rating ? 'text-yellow-500' : 'text-gray-300'}`}
                                    >
                                      ⭐
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                        
                        {interaction.context && (
                          <div className="mt-2 text-xs text-gray-500">
                            {interaction.context.source && (
                              <span>Source: {interaction.context.source}</span>
                            )}
                            {interaction.context.page && (
                              <span className="ml-2">Page: {interaction.context.page}</span>
                            )}
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </motion.div>

      {/* Learning Insights */}
      {analytics && analytics.insights && (
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-purple-600" />
                <span>Learning Insights</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.insights.most_active_time && (
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-1">Peak Learning Time</h4>
                    <p className="text-sm text-blue-700">
                      You're most active during {analytics.insights.most_active_time}
                    </p>
                  </div>
                )}
                
                {analytics.insights.preferred_content_type && (
                  <div className="p-3 bg-green-50 rounded-lg">
                    <h4 className="font-medium text-green-900 mb-1">Preferred Content Type</h4>
                    <p className="text-sm text-green-700">
                      You engage most with {analytics.insights.preferred_content_type} content
                    </p>
                  </div>
                )}
                
                {analytics.insights.completion_rate && (
                  <div className="p-3 bg-purple-50 rounded-lg">
                    <h4 className="font-medium text-purple-900 mb-1">Completion Rate</h4>
                    <div className="flex items-center space-x-2">
                      <Progress value={analytics.insights.completion_rate} className="flex-1" />
                      <span className="text-sm text-purple-700">
                        {Math.round(analytics.insights.completion_rate)}%
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Export Data */}
      <motion.div variants={itemVariants}>
        <Card className="border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">Export Learning Data</h4>
                <p className="text-sm text-gray-600">
                  Download your learning history and analytics data
                </p>
              </div>
              <Button variant="outline" onClick={() => {
                // TODO: Implement data export functionality
                console.log('Exporting learning data...');
              }}>
                <Download className="h-4 w-4 mr-2" />
                Export Data
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}