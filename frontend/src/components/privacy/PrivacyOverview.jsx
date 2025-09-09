/**
 * Privacy Overview Component
 * High-level privacy status and quick controls
 */

'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/useToast';
import { 
  Shield, 
  Eye, 
  Database, 
  Users, 
  Activity, 
  CheckCircle, 
  AlertCircle, 
  Info 
} from 'lucide-react';

const PrivacyOverview = ({ data, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const privacyScore = data?.privacy_score || 0;
  const consentStatus = data?.consent_status || {};
  const dataCollection = data?.data_collection || {};

  const handleQuickToggle = async (setting, value) => {
    setLoading(true);
    try {
      const response = await fetch('/api/preferences/privacy-quick-toggle/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          setting,
          value
        }),
      });

      if (!response.ok) throw new Error('Failed to update setting');

      const result = await response.json();
      onUpdate(result.privacy_data);

      toast({
        title: 'Privacy Setting Updated',
        description: `${setting} has been ${value ? 'enabled' : 'disabled'}.`,
      });

    } catch (error) {
      console.error('Error updating privacy setting:', error);
      toast({
        title: 'Error',
        description: 'Failed to update privacy setting. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const getPrivacyScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPrivacyLevel = (score) => {
    if (score >= 80) return { level: 'High', color: 'bg-green-100 text-green-800' };
    if (score >= 60) return { level: 'Medium', color: 'bg-yellow-100 text-yellow-800' };
    return { level: 'Low', color: 'bg-red-100 text-red-800' };
  };

  return (
    <div className="space-y-6">
      {/* Privacy Score Card */}
      <Card className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-full">
              <Shield className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Privacy Score</h2>
              <p className="text-gray-600">Your overall privacy protection level</p>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-3xl font-bold ${getPrivacyScoreColor(privacyScore)}`}>
              {privacyScore}%
            </div>
            <Badge className={getPrivacyLevel(privacyScore).color}>
              {getPrivacyLevel(privacyScore).level} Protection
            </Badge>
          </div>
        </div>
        <Progress value={privacyScore} className="h-3 mb-4" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>Consent Active</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>Data Encrypted</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>GDPR Compliant</span>
          </div>
          <div className="flex items-center gap-2">
            <Info className="w-4 h-4 text-blue-500" />
            <span>Audit Enabled</span>
          </div>
        </div>
      </Card>

      {/* Quick Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Analytics Consent */}
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <Activity className="w-5 h-5 text-blue-600" />
              <div>
                <h3 className="font-semibold">Analytics</h3>
                <p className="text-sm text-gray-600">Learning behavior tracking</p>
              </div>
            </div>
            <Switch
              checked={consentStatus.analytics_consent || false}
              onCheckedChange={(value) => handleQuickToggle('analytics_consent', value)}
              disabled={loading}
            />
          </div>
          <div className="text-sm text-gray-600">
            Helps personalize your learning experience and improve our platform.
          </div>
        </Card>

        {/* Behavioral Analysis */}
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <Eye className="w-5 h-5 text-purple-600" />
              <div>
                <h3 className="font-semibold">Behavioral Analysis</h3>
                <p className="text-sm text-gray-600">Advanced pattern detection</p>
              </div>
            </div>
            <Switch
              checked={consentStatus.behavioral_analysis || false}
              onCheckedChange={(value) => handleQuickToggle('behavioral_analysis', value)}
              disabled={loading}
            />
          </div>
          <div className="text-sm text-gray-600">
            Enables AI-powered recommendations and dropout risk prevention.
          </div>
        </Card>

        {/* Personalization */}
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <Users className="w-5 h-5 text-green-600" />
              <div>
                <h3 className="font-semibold">Personalization</h3>
                <p className="text-sm text-gray-600">Content customization</p>
              </div>
            </div>
            <Switch
              checked={consentStatus.personalization_consent || false}
              onCheckedChange={(value) => handleQuickToggle('personalization_consent', value)}
              disabled={loading}
            />
          </div>
          <div className="text-sm text-gray-600">
            Customizes course recommendations and learning paths for you.
          </div>
        </Card>
      </div>

      {/* Data Collection Summary */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Database className="w-5 h-5" />
          Data Collection Summary
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {dataCollection.profile_data_points || 0}
            </div>
            <div className="text-sm text-gray-600">Profile Data Points</div>
            <div className="text-xs text-gray-500 mt-1">
              Name, email, preferences, etc.
            </div>
          </div>
          
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {dataCollection.learning_interactions || 0}
            </div>
            <div className="text-sm text-gray-600">Learning Interactions</div>
            <div className="text-xs text-gray-500 mt-1">
              Courses, quizzes, progress tracking
            </div>
          </div>
          
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {dataCollection.social_connections || 0}
            </div>
            <div className="text-sm text-gray-600">Social Connections</div>
            <div className="text-xs text-gray-500 mt-1">
              Connected accounts and profile data
            </div>
          </div>
          
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {dataCollection.analytics_events || 0}
            </div>
            <div className="text-sm text-gray-600">Analytics Events</div>
            <div className="text-xs text-gray-500 mt-1">
              Clicks, views, time tracking
            </div>
          </div>
        </div>
      </Card>

      {/* Recent Privacy Activity */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Privacy Activity</h3>
        <div className="space-y-3">
          {data?.recent_activity?.map((activity, index) => (
            <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <div className="font-medium text-sm">{activity.action}</div>
                <div className="text-xs text-gray-600">{activity.description}</div>
              </div>
              <div className="text-xs text-gray-500">
                {new Date(activity.timestamp).toLocaleDateString()}
              </div>
            </div>
          )) || (
            <div className="text-center text-gray-500 py-4">
              No recent privacy activity
            </div>
          )}
        </div>
      </Card>

      {/* Privacy Recommendations */}
      {data?.recommendations?.length > 0 && (
        <Card className="p-6 border-yellow-200 bg-yellow-50">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-yellow-600" />
            Privacy Recommendations
          </h3>
          <div className="space-y-3">
            {data.recommendations.map((rec, index) => (
              <div key={index} className="flex items-start gap-3">
                <Info className="w-4 h-4 text-yellow-600 mt-1" />
                <div className="flex-1">
                  <div className="font-medium text-sm">{rec.title}</div>
                  <div className="text-sm text-gray-600">{rec.description}</div>
                  {rec.action && (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="mt-2 border-yellow-300 text-yellow-700 hover:bg-yellow-100"
                      onClick={() => rec.action()}
                    >
                      {rec.action_text}
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default PrivacyOverview;