/**
 * Data Collection Settings Component
 * Granular controls for different types of data collection
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/useToast';
import { 
  Database, 
  Activity, 
  Users, 
  Brain, 
  MapPin, 
  Camera, 
  Mic,
  Clock,
  Info,
  Save,
  RefreshCw
} from 'lucide-react';

const DataCollectionSettings = ({ data, onUpdate }) => {
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (data?.collection_settings) {
      setSettings(data.collection_settings);
    }
  }, [data]);

  const handleSettingChange = (category, setting, value) => {
    const newSettings = {
      ...settings,
      [category]: {
        ...settings[category],
        [setting]: value
      }
    };
    setSettings(newSettings);
    setHasChanges(true);
  };

  const saveSettings = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/preferences/data-collection-settings/', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ settings }),
      });

      if (!response.ok) throw new Error('Failed to save settings');

      const result = await response.json();
      onUpdate(result);
      setHasChanges(false);

      toast({
        title: 'Settings Saved',
        description: 'Your data collection preferences have been updated.',
      });

    } catch (error) {
      console.error('Error saving settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to save settings. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const resetToDefaults = () => {
    const defaultSettings = {
      learning_analytics: {
        enabled: true,
        granularity: 'medium',
        include_timing: true,
        include_errors: true,
        retention_days: 365
      },
      behavioral_tracking: {
        enabled: false,
        mouse_tracking: false,
        scroll_tracking: true,
        click_tracking: true,
        session_recording: false
      },
      performance_monitoring: {
        enabled: true,
        page_load_times: true,
        interaction_delays: true,
        error_tracking: true,
        crash_reporting: true
      },
      location_data: {
        enabled: false,
        timezone_only: true,
        city_level: false,
        precise_location: false
      },
      device_fingerprinting: {
        enabled: true,
        basic_info: true,
        detailed_specs: false,
        browser_plugins: false
      }
    };
    setSettings(defaultSettings);
    setHasChanges(true);
  };

  const dataCollectionCategories = [
    {
      id: 'learning_analytics',
      title: 'Learning Analytics',
      description: 'Track learning progress, quiz scores, and course interactions',
      icon: Activity,
      color: 'text-blue-600',
      settings: [
        {
          key: 'enabled',
          label: 'Enable Learning Analytics',
          type: 'switch',
          description: 'Track your learning progress and performance'
        },
        {
          key: 'granularity',
          label: 'Data Granularity',
          type: 'select',
          options: [
            { value: 'low', label: 'Low - Basic progress only' },
            { value: 'medium', label: 'Medium - Detailed interactions' },
            { value: 'high', label: 'High - Complete activity log' }
          ],
          description: 'How detailed should the learning data collection be?'
        },
        {
          key: 'include_timing',
          label: 'Time Tracking',
          type: 'switch',
          description: 'Record time spent on activities and courses'
        },
        {
          key: 'include_errors',
          label: 'Error Analysis',
          type: 'switch',
          description: 'Track mistakes to help improve learning'
        },
        {
          key: 'retention_days',
          label: 'Data Retention (days)',
          type: 'slider',
          min: 30,
          max: 1095,
          step: 30,
          description: 'How long to keep your learning analytics data'
        }
      ]
    },
    {
      id: 'behavioral_tracking',
      title: 'Behavioral Tracking',
      description: 'Monitor user interface interactions and usage patterns',
      icon: Users,
      color: 'text-purple-600',
      settings: [
        {
          key: 'enabled',
          label: 'Enable Behavioral Tracking',
          type: 'switch',
          description: 'Track how you interact with the platform'
        },
        {
          key: 'mouse_tracking',
          label: 'Mouse Movement',
          type: 'switch',
          description: 'Record mouse movements for UX improvements'
        },
        {
          key: 'scroll_tracking',
          label: 'Scroll Behavior',
          type: 'switch',
          description: 'Track scrolling patterns and reading time'
        },
        {
          key: 'click_tracking',
          label: 'Click Events',
          type: 'switch',
          description: 'Record button clicks and interactions'
        },
        {
          key: 'session_recording',
          label: 'Session Recording',
          type: 'switch',
          description: 'Record full user sessions (anonymized)'
        }
      ]
    },
    {
      id: 'performance_monitoring',
      title: 'Performance Monitoring',
      description: 'Collect data to improve platform speed and reliability',
      icon: RefreshCw,
      color: 'text-green-600',
      settings: [
        {
          key: 'enabled',
          label: 'Enable Performance Monitoring',
          type: 'switch',
          description: 'Help us improve platform performance'
        },
        {
          key: 'page_load_times',
          label: 'Page Load Tracking',
          type: 'switch',
          description: 'Record how quickly pages load'
        },
        {
          key: 'interaction_delays',
          label: 'Response Time Tracking',
          type: 'switch',
          description: 'Monitor delays in user interactions'
        },
        {
          key: 'error_tracking',
          label: 'Error Reporting',
          type: 'switch',
          description: 'Report errors to help fix issues'
        },
        {
          key: 'crash_reporting',
          label: 'Crash Analytics',
          type: 'switch',
          description: 'Report application crashes'
        }
      ]
    },
    {
      id: 'location_data',
      title: 'Location Data',
      description: 'Geographic information for localized content',
      icon: MapPin,
      color: 'text-red-600',
      settings: [
        {
          key: 'enabled',
          label: 'Enable Location Data',
          type: 'switch',
          description: 'Allow location-based features'
        },
        {
          key: 'timezone_only',
          label: 'Timezone Only',
          type: 'switch',
          description: 'Share only your timezone'
        },
        {
          key: 'city_level',
          label: 'City-Level Location',
          type: 'switch',
          description: 'Share your approximate city'
        },
        {
          key: 'precise_location',
          label: 'Precise Location',
          type: 'switch',
          description: 'Share exact GPS coordinates'
        }
      ]
    },
    {
      id: 'device_fingerprinting',
      title: 'Device Information',
      description: 'Technical details about your device and browser',
      icon: Camera,
      color: 'text-orange-600',
      settings: [
        {
          key: 'enabled',
          label: 'Enable Device Fingerprinting',
          type: 'switch',
          description: 'Collect device information for security'
        },
        {
          key: 'basic_info',
          label: 'Basic Device Info',
          type: 'switch',
          description: 'Browser type, screen resolution, OS'
        },
        {
          key: 'detailed_specs',
          label: 'Detailed Specifications',
          type: 'switch',
          description: 'Hardware details and capabilities'
        },
        {
          key: 'browser_plugins',
          label: 'Browser Plugins',
          type: 'switch',
          description: 'List of installed browser extensions'
        }
      ]
    }
  ];

  const renderSetting = (category, setting) => {
    const value = settings[category.id]?.[setting.key];

    switch (setting.type) {
      case 'switch':
        return (
          <Switch
            checked={value || false}
            onCheckedChange={(newValue) => 
              handleSettingChange(category.id, setting.key, newValue)
            }
          />
        );
      
      case 'select':
        return (
          <Select
            value={value || setting.options[0].value}
            onValueChange={(newValue) => 
              handleSettingChange(category.id, setting.key, newValue)
            }
          >
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {setting.options.map(option => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );
      
      case 'slider':
        return (
          <div className="w-48">
            <Slider
              value={[value || setting.min]}
              onValueChange={([newValue]) => 
                handleSettingChange(category.id, setting.key, newValue)
              }
              min={setting.min}
              max={setting.max}
              step={setting.step}
              className="mb-2"
            />
            <div className="text-sm text-gray-600 text-center">
              {value || setting.min} {setting.unit || 'days'}
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Data Collection Settings</h2>
          <p className="text-gray-600">
            Control what data we collect and how it's used to improve your experience
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={resetToDefaults}>
            Reset to Defaults
          </Button>
          <Button 
            onClick={saveSettings} 
            disabled={!hasChanges || loading}
          >
            <Save className="w-4 h-4 mr-2" />
            {loading ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>

      {/* Data Collection Categories */}
      <div className="space-y-6">
        {dataCollectionCategories.map((category) => {
          const Icon = category.icon;
          const isEnabled = settings[category.id]?.enabled !== false;

          return (
            <Card key={category.id} className="p-6">
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-full bg-gray-100 ${category.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <h3 className="text-lg font-semibold">{category.title}</h3>
                      <p className="text-gray-600">{category.description}</p>
                    </div>
                    <Badge variant={isEnabled ? 'default' : 'secondary'}>
                      {isEnabled ? 'Active' : 'Disabled'}
                    </Badge>
                  </div>

                  <div className="space-y-4 mt-6">
                    {category.settings.map((setting, index) => (
                      <div key={setting.key} className="flex items-center justify-between py-3 border-b last:border-b-0">
                        <div className="flex-1 pr-6">
                          <div className="flex items-center gap-2 mb-1">
                            <label className="font-medium text-sm">
                              {setting.label}
                            </label>
                            {setting.key === 'session_recording' && (
                              <Badge variant="destructive" className="text-xs">
                                High Privacy Impact
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-gray-600">
                            {setting.description}
                          </p>
                        </div>
                        <div className="flex items-center gap-3">
                          {renderSetting(category, setting)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Data Impact Summary */}
      <Card className="p-6 bg-blue-50 border-blue-200">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-600 mt-1" />
          <div>
            <h3 className="font-semibold text-blue-900 mb-2">
              How This Data Helps You
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="font-medium mb-1">Personalized Learning</h4>
                <p className="text-blue-700">
                  Your learning analytics help us recommend courses and adjust difficulty
                </p>
              </div>
              <div>
                <h4 className="font-medium mb-1">Performance Optimization</h4>
                <p className="text-blue-700">
                  Performance data helps us make the platform faster and more reliable
                </p>
              </div>
              <div>
                <h4 className="font-medium mb-1">Better User Experience</h4>
                <p className="text-blue-700">
                  Behavioral tracking shows us what features work best
                </p>
              </div>
              <div>
                <h4 className="font-medium mb-1">Security & Fraud Prevention</h4>
                <p className="text-blue-700">
                  Device fingerprinting helps protect your account from unauthorized access
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Save Reminder */}
      {hasChanges && (
        <Card className="p-4 border-yellow-200 bg-yellow-50">
          <div className="flex items-center gap-3">
            <Clock className="w-5 h-5 text-yellow-600" />
            <div className="flex-1">
              <p className="text-yellow-800 font-medium">
                You have unsaved changes
              </p>
              <p className="text-yellow-700 text-sm">
                Don't forget to save your data collection preferences
              </p>
            </div>
            <Button onClick={saveSettings} disabled={loading}>
              Save Now
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};

export default DataCollectionSettings;