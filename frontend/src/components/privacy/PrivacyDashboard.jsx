/**
 * Privacy Dashboard - Main interface for user privacy controls
 * Comprehensive privacy management with granular settings and GDPR compliance
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/useToast';
import { Shield, Download, Trash2, Eye, Settings, AlertTriangle } from 'lucide-react';

import PrivacyOverview from './PrivacyOverview';
import DataCollectionSettings from './DataCollectionSettings';
import ConsentManagement from './ConsentManagement';
import DataExportDownload from './DataExportDownload';
import PrivacyAuditLog from './PrivacyAuditLog';
import SocialPrivacyControls from './SocialPrivacyControls';
import DataRetentionSettings from './DataRetentionSettings';

const PrivacyDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [privacyData, setPrivacyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadPrivacyData();
  }, []);

  const loadPrivacyData = async () => {
    try {
      setLoading(true);
      
      // Fetch privacy overview data
      const overviewResponse = await fetch('/api/preferences/privacy-overview/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!overviewResponse.ok) throw new Error('Failed to load privacy data');
      
      const data = await overviewResponse.json();
      setPrivacyData(data);
      
    } catch (error) {
      console.error('Error loading privacy data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load privacy settings. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePrivacyUpdate = (updates) => {
    setPrivacyData(prev => ({
      ...prev,
      ...updates
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Shield className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Privacy Center</h1>
            <p className="text-gray-600">
              Manage your privacy settings and control how your data is used
            </p>
          </div>
        </div>

        {/* Privacy Status Banner */}
        <Card className="p-4 bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="font-medium text-green-800">
                Privacy Protection Active
              </span>
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                {privacyData?.overall_privacy_level || 'Standard'} Level
              </Badge>
            </div>
            <div className="text-sm text-gray-600">
              Last updated: {privacyData?.last_updated ? 
                new Date(privacyData.last_updated).toLocaleDateString() : 'Never'
              }
            </div>
          </div>
        </Card>
      </div>

      {/* Privacy Controls Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-7 lg:w-fit lg:grid-cols-7">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <Eye className="w-4 h-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="collection" className="flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Data Collection
          </TabsTrigger>
          <TabsTrigger value="consent" className="flex items-center gap-2">
            <Shield className="w-4 h-4" />
            Consent
          </TabsTrigger>
          <TabsTrigger value="social" className="flex items-center gap-2">
            Social
          </TabsTrigger>
          <TabsTrigger value="retention" className="flex items-center gap-2">
            Retention
          </TabsTrigger>
          <TabsTrigger value="export" className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </TabsTrigger>
          <TabsTrigger value="audit" className="flex items-center gap-2">
            Audit Log
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <PrivacyOverview 
            data={privacyData} 
            onUpdate={handlePrivacyUpdate}
          />
        </TabsContent>

        <TabsContent value="collection" className="space-y-6">
          <DataCollectionSettings 
            data={privacyData} 
            onUpdate={handlePrivacyUpdate}
          />
        </TabsContent>

        <TabsContent value="consent" className="space-y-6">
          <ConsentManagement 
            data={privacyData} 
            onUpdate={handlePrivacyUpdate}
          />
        </TabsContent>

        <TabsContent value="social" className="space-y-6">
          <SocialPrivacyControls 
            data={privacyData} 
            onUpdate={handlePrivacyUpdate}
          />
        </TabsContent>

        <TabsContent value="retention" className="space-y-6">
          <DataRetentionSettings 
            data={privacyData} 
            onUpdate={handlePrivacyUpdate}
          />
        </TabsContent>

        <TabsContent value="export" className="space-y-6">
          <DataExportDownload 
            data={privacyData} 
            onRefresh={loadPrivacyData}
          />
        </TabsContent>

        <TabsContent value="audit" className="space-y-6">
          <PrivacyAuditLog />
        </TabsContent>
      </Tabs>

      {/* Emergency Controls */}
      <Card className="mt-8 border-red-200 bg-red-50">
        <div className="p-6">
          <div className="flex items-start gap-4">
            <AlertTriangle className="w-6 h-6 text-red-600 mt-1" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-red-900 mb-2">
                Emergency Privacy Controls
              </h3>
              <p className="text-red-700 mb-4">
                Use these controls if you need immediate privacy protection or want to 
                completely remove your data from our systems.
              </p>
              <div className="flex gap-3">
                <Button 
                  variant="outline" 
                  className="border-red-300 text-red-700 hover:bg-red-100"
                  onClick={() => setActiveTab('export')}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download All Data
                </Button>
                <Button 
                  variant="destructive"
                  className="bg-red-600 hover:bg-red-700"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete My Account
                </Button>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default PrivacyDashboard;