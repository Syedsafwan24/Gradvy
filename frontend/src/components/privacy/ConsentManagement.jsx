/**
 * Consent Management Component
 * GDPR-compliant consent tracking and management
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { useToast } from '@/hooks/useToast';
import { 
  Shield, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  FileText, 
  Download,
  RefreshCw,
  Trash2,
  Info
} from 'lucide-react';

const ConsentManagement = ({ data, onUpdate }) => {
  const [consents, setConsents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [updatingConsent, setUpdatingConsent] = useState(null);
  const { toast } = useToast();

  useEffect(() => {
    if (data?.consent_records) {
      setConsents(data.consent_records);
    }
  }, [data]);

  const updateConsent = async (consentId, granted) => {
    setUpdatingConsent(consentId);
    try {
      const response = await fetch(`/api/preferences/consent/${consentId}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ granted }),
      });

      if (!response.ok) throw new Error('Failed to update consent');

      const result = await response.json();
      
      // Update local state
      setConsents(prev => prev.map(consent => 
        consent.id === consentId ? { ...consent, ...result.consent } : consent
      ));

      onUpdate(result.privacy_data);

      toast({
        title: 'Consent Updated',
        description: `Consent has been ${granted ? 'granted' : 'withdrawn'}.`,
      });

    } catch (error) {
      console.error('Error updating consent:', error);
      toast({
        title: 'Error',
        description: 'Failed to update consent. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setUpdatingConsent(null);
    }
  };

  const revokeAllConsents = async () => {
    if (!confirm('Are you sure you want to revoke all consents? This will severely limit your experience on the platform.')) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/preferences/consent/revoke-all/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to revoke consents');

      const result = await response.json();
      setConsents(result.consent_records);
      onUpdate(result.privacy_data);

      toast({
        title: 'All Consents Revoked',
        description: 'You have withdrawn consent for all data processing activities.',
        variant: 'destructive',
      });

    } catch (error) {
      console.error('Error revoking consents:', error);
      toast({
        title: 'Error',
        description: 'Failed to revoke consents. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const downloadConsentHistory = async () => {
    try {
      const response = await fetch('/api/preferences/consent-history/download/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to download consent history');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'consent-history.pdf';
      link.click();
      window.URL.revokeObjectURL(url);

      toast({
        title: 'Download Started',
        description: 'Your consent history is being downloaded.',
      });

    } catch (error) {
      console.error('Error downloading consent history:', error);
      toast({
        title: 'Error',
        description: 'Failed to download consent history.',
        variant: 'destructive',
      });
    }
  };

  const getConsentStatusBadge = (consent) => {
    if (!consent.granted) {
      return <Badge variant="destructive">Withdrawn</Badge>;
    }
    
    if (consent.expires_at) {
      const expiryDate = new Date(consent.expires_at);
      const now = new Date();
      const daysUntilExpiry = Math.ceil((expiryDate - now) / (1000 * 60 * 60 * 24));
      
      if (daysUntilExpiry <= 30) {
        return <Badge variant="destructive">Expires Soon ({daysUntilExpiry}d)</Badge>;
      }
    }
    
    return <Badge variant="default">Active</Badge>;
  };

  const consentTypes = [
    {
      id: 'analytics',
      title: 'Analytics & Performance',
      description: 'Collection of usage data, performance metrics, and anonymous analytics to improve our services',
      purpose: 'Service improvement and optimization',
      required: false,
      dataTypes: ['Page views', 'Click events', 'Performance metrics', 'Error reports'],
      retention: '2 years',
      thirdParties: ['Google Analytics', 'Sentry']
    },
    {
      id: 'personalization',
      title: 'Personalization & Recommendations',
      description: 'Processing of your learning data to provide personalized course recommendations and content',
      purpose: 'Enhanced user experience and personalized content delivery',
      required: false,
      dataTypes: ['Course progress', 'Quiz results', 'Learning preferences', 'Time spent'],
      retention: '3 years',
      thirdParties: ['Internal ML systems']
    },
    {
      id: 'marketing',
      title: 'Marketing Communications',
      description: 'Use of your contact information for promotional emails and targeted advertising',
      purpose: 'Marketing and promotional communications',
      required: false,
      dataTypes: ['Email address', 'Name', 'Course interests', 'Engagement history'],
      retention: '5 years or until withdrawal',
      thirdParties: ['Mailchimp', 'Facebook Ads', 'Google Ads']
    },
    {
      id: 'social_data',
      title: 'Social Media Integration',
      description: 'Collection and processing of data from connected social media accounts',
      purpose: 'Profile enrichment and social features',
      required: false,
      dataTypes: ['Profile information', 'Professional history', 'Skills', 'Connections'],
      retention: '1 year',
      thirdParties: ['LinkedIn API', 'GitHub API', 'Google API']
    },
    {
      id: 'behavioral_analysis',
      title: 'Advanced Behavioral Analysis',
      description: 'Deep analysis of learning patterns for dropout prevention and adaptive learning',
      purpose: 'AI-powered learning optimization and risk prevention',
      required: false,
      dataTypes: ['Learning velocity', 'Engagement patterns', 'Difficulty progression', 'Help-seeking behavior'],
      retention: '2 years',
      thirdParties: ['Internal AI systems']
    },
    {
      id: 'essential',
      title: 'Essential Services',
      description: 'Basic data processing necessary for core platform functionality',
      purpose: 'Core service delivery and account management',
      required: true,
      dataTypes: ['Account information', 'Authentication data', 'Basic preferences'],
      retention: 'Account lifetime',
      thirdParties: ['Authentication services']
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Consent Management</h2>
          <p className="text-gray-600">
            Manage your data processing consents and understand your rights
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={downloadConsentHistory}>
            <Download className="w-4 h-4 mr-2" />
            Download History
          </Button>
          <Button 
            variant="destructive" 
            onClick={revokeAllConsents}
            disabled={loading}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            {loading ? 'Revoking...' : 'Revoke All'}
          </Button>
        </div>
      </div>

      {/* Consent Overview */}
      <Card className="p-6 bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
        <div className="flex items-center gap-4 mb-4">
          <Shield className="w-8 h-8 text-green-600" />
          <div>
            <h3 className="text-lg font-semibold text-green-800">Your Rights Under GDPR</h3>
            <p className="text-green-700">
              You have full control over how your personal data is processed
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center gap-2 text-green-700">
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm">Right to withdraw consent</span>
          </div>
          <div className="flex items-center gap-2 text-green-700">
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm">Right to access your data</span>
          </div>
          <div className="flex items-center gap-2 text-green-700">
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm">Right to data portability</span>
          </div>
        </div>
      </Card>

      {/* Consent Categories */}
      <div className="space-y-4">
        {consentTypes.map((type) => {
          const consent = consents.find(c => c.consent_type === type.id);
          const isGranted = consent?.granted ?? false;
          const isUpdating = updatingConsent === consent?.id;

          return (
            <Card key={type.id} className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold">{type.title}</h3>
                    {getConsentStatusBadge(consent)}
                    {type.required && (
                      <Badge variant="secondary">Required</Badge>
                    )}
                  </div>
                  <p className="text-gray-600 mb-3">{type.description}</p>
                  
                  {/* Consent Details */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <h4 className="font-medium mb-1 text-gray-800">Purpose</h4>
                      <p className="text-gray-600">{type.purpose}</p>
                    </div>
                    <div>
                      <h4 className="font-medium mb-1 text-gray-800">Data Types</h4>
                      <div className="flex flex-wrap gap-1">
                        {type.dataTypes.map(dataType => (
                          <Badge key={dataType} variant="outline" className="text-xs">
                            {dataType}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium mb-1 text-gray-800">Retention Period</h4>
                      <p className="text-gray-600">{type.retention}</p>
                    </div>
                    <div>
                      <h4 className="font-medium mb-1 text-gray-800">Third Parties</h4>
                      <div className="flex flex-wrap gap-1">
                        {type.thirdParties.map(party => (
                          <Badge key={party} variant="outline" className="text-xs">
                            {party}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="ml-6 flex flex-col items-center gap-2">
                  <Switch
                    checked={isGranted}
                    onCheckedChange={(value) => updateConsent(consent?.id, value)}
                    disabled={type.required || isUpdating}
                  />
                  {isUpdating && (
                    <RefreshCw className="w-4 h-4 animate-spin text-gray-400" />
                  )}
                </div>
              </div>

              {/* Consent History */}
              {consent && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-medium mb-2 flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    Consent History
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Granted:</span>
                      <div className="font-medium">
                        {consent.granted_at ? new Date(consent.granted_at).toLocaleDateString() : 'Never'}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600">Last Updated:</span>
                      <div className="font-medium">
                        {consent.updated_at ? new Date(consent.updated_at).toLocaleDateString() : 'Never'}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600">Expires:</span>
                      <div className="font-medium">
                        {consent.expires_at ? new Date(consent.expires_at).toLocaleDateString() : 'Never'}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </Card>
          );
        })}
      </div>

      {/* Consent Renewal Reminder */}
      <Card className="p-6 border-yellow-200 bg-yellow-50">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 mt-1" />
          <div>
            <h3 className="font-semibold text-yellow-800 mb-2">
              Consent Renewal
            </h3>
            <p className="text-yellow-700 mb-3">
              Some of your consents may expire after a certain period. We'll notify you 
              before expiration and ask for renewal to continue providing personalized services.
            </p>
            <div className="text-sm text-yellow-600">
              Next renewal check: {data?.next_consent_review || 'Not scheduled'}
            </div>
          </div>
        </div>
      </Card>

      {/* Legal Information */}
      <Card className="p-6">
        <div className="flex items-start gap-3">
          <FileText className="w-5 h-5 text-blue-600 mt-1" />
          <div>
            <h3 className="font-semibold text-blue-800 mb-2">
              Legal Basis for Processing
            </h3>
            <div className="space-y-2 text-sm text-gray-700">
              <p>
                <strong>Consent:</strong> We process your personal data based on your explicit consent 
                for non-essential services like analytics and marketing.
              </p>
              <p>
                <strong>Legitimate Interest:</strong> We process certain data for legitimate business 
                interests like security, fraud prevention, and service improvement.
              </p>
              <p>
                <strong>Contract:</strong> Some processing is necessary to fulfill our service 
                agreement with you, such as account management and course delivery.
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Data Subject Rights */}
      <Card className="p-6">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-green-600 mt-1" />
          <div>
            <h3 className="font-semibold text-green-800 mb-2">
              Your Data Subject Rights
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="font-medium mb-1">Right to Access</h4>
                <p className="text-gray-600">Request a copy of your personal data</p>
              </div>
              <div>
                <h4 className="font-medium mb-1">Right to Rectification</h4>
                <p className="text-gray-600">Correct inaccurate personal data</p>
              </div>
              <div>
                <h4 className="font-medium mb-1">Right to Erasure</h4>
                <p className="text-gray-600">Request deletion of your personal data</p>
              </div>
              <div>
                <h4 className="font-medium mb-1">Right to Portability</h4>
                <p className="text-gray-600">Receive your data in a machine-readable format</p>
              </div>
              <div>
                <h4 className="font-medium mb-1">Right to Object</h4>
                <p className="text-gray-600">Object to processing for direct marketing</p>
              </div>
              <div>
                <h4 className="font-medium mb-1">Right to Restrict</h4>
                <p className="text-gray-600">Limit how we process your data</p>
              </div>
            </div>
            <div className="mt-4">
              <Button variant="outline" size="sm">
                Contact Data Protection Officer
              </Button>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ConsentManagement;