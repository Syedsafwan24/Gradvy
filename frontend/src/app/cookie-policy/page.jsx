'use client';

/**
 * Cookie Policy Page
 * Comprehensive cookie policy and information page
 */

import { useState } from 'react';
import { Shield, BarChart3, Zap, Target, Settings, ExternalLink } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { COOKIE_POLICY_DATA, COOKIE_TYPES, getCookiePreferences, CookieBanner } from '../../lib/cookieUtils';

const CookiePolicyPage = () => {
  const [preferences] = useState(getCookiePreferences());

  const handleOpenPreferences = () => {
    CookieBanner.openPreferences();
  };

  const getCookieIcon = (type) => {
    switch (type) {
      case COOKIE_TYPES.ESSENTIAL:
        return <Shield className="w-8 h-8 text-green-600" />;
      case COOKIE_TYPES.ANALYTICS:
        return <BarChart3 className="w-8 h-8 text-blue-600" />;
      case COOKIE_TYPES.FUNCTIONAL:
        return <Zap className="w-8 h-8 text-purple-600" />;
      case COOKIE_TYPES.MARKETING:
        return <Target className="w-8 h-8 text-orange-600" />;
      default:
        return <Shield className="w-8 h-8 text-gray-600" />;
    }
  };

  const getStatusBadge = (cookieType) => {
    const isEnabled = preferences[cookieType];
    
    if (cookieType === COOKIE_TYPES.ESSENTIAL) {
      return (
        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
          Always Active
        </span>
      );
    }
    
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
        isEnabled 
          ? 'bg-green-100 text-green-800' 
          : 'bg-gray-100 text-gray-800'
      }`}>
        {isEnabled ? 'Enabled' : 'Disabled'}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              🍪 Cookie Policy
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Learn about how Gradvy uses cookies to enhance your learning experience, 
              improve our services, and protect your privacy.
            </p>
            <div className="mt-6">
              <Button
                onClick={handleOpenPreferences}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 inline-flex items-center gap-2"
              >
                <Settings className="w-5 h-5" />
                Manage Cookie Preferences
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Overview */}
        <section className="mb-12">
          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">What are cookies?</h2>
            <div className="prose max-w-none text-gray-700">
              <p className="mb-4">
                Cookies are small text files that are stored on your device (computer, smartphone, or tablet) 
                when you visit our website. They help us recognize you, remember your preferences, and improve 
                your overall experience on Gradvy.
              </p>
              <p className="mb-4">
                We use cookies for various purposes, including essential site functionality, analytics, 
                personalization, and security. This policy explains what types of cookies we use, 
                why we use them, and how you can control them.
              </p>
            </div>
          </div>
        </section>

        {/* Cookie Types */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Types of cookies we use</h2>
          <div className="space-y-6">
            {Object.entries(COOKIE_POLICY_DATA).map(([cookieType, data]) => (
              <div key={cookieType} className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    {getCookieIcon(cookieType)}
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900">{data.name}</h3>
                      <div className="mt-2">
                        {getStatusBadge(cookieType)}
                      </div>
                    </div>
                  </div>
                </div>
                
                <p className="text-gray-700 mb-4 leading-relaxed">
                  {data.description}
                </p>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Examples:</h4>
                    <ul className="space-y-2">
                      {data.examples.map((example, index) => (
                        <li key={index} className="flex items-center text-sm text-gray-700">
                          <span className="w-2 h-2 bg-blue-500 rounded-full mr-3 flex-shrink-0" />
                          {example}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Retention Period:</h4>
                    <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                      {data.duration}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* How to Control Cookies */}
        <section className="mb-12">
          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">How to control cookies</h2>
            
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Through Gradvy Settings</h3>
                <p className="text-gray-700 mb-4">
                  You can manage your cookie preferences directly on our website using our cookie preference center.
                </p>
                <Button
                  onClick={handleOpenPreferences}
                  variant="outline"
                  className="inline-flex items-center gap-2"
                >
                  <Settings className="w-4 h-4" />
                  Open Cookie Preferences
                </Button>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Through Your Browser</h3>
                <p className="text-gray-700 mb-4">
                  Most web browsers allow you to control cookies through their settings. Here are links to 
                  cookie settings for popular browsers:
                </p>
                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {[
                    { name: 'Chrome', url: 'https://support.google.com/chrome/answer/95647' },
                    { name: 'Firefox', url: 'https://support.mozilla.org/en-US/kb/cookies-information-websites-store-on-your-computer' },
                    { name: 'Safari', url: 'https://support.apple.com/guide/safari/manage-cookies-and-website-data-sfri11471/mac' },
                    { name: 'Edge', url: 'https://support.microsoft.com/en-us/help/4027947/microsoft-edge-delete-cookies' }
                  ].map((browser) => (
                    <a
                      key={browser.name}
                      href={browser.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
                    >
                      <span className="font-medium text-gray-900">{browser.name}</span>
                      <ExternalLink className="w-4 h-4 text-gray-500" />
                    </a>
                  ))}
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h4 className="font-medium text-yellow-800 mb-2">⚠️ Important Note</h4>
                <p className="text-sm text-yellow-700">
                  Disabling certain cookies may impact your experience on Gradvy. Essential cookies 
                  cannot be disabled as they are required for basic site functionality, including 
                  security features and user authentication.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Third-Party Cookies */}
        <section className="mb-12">
          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Third-party cookies</h2>
            <div className="prose max-w-none text-gray-700">
              <p className="mb-4">
                We may use third-party services that set cookies on your device. These services 
                have their own privacy policies and cookie practices:
              </p>
              
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Third-party services we may use:</h3>
                <ul className="space-y-3">
                  <li className="flex items-start">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-3 mt-2 flex-shrink-0" />
                    <div>
                      <strong>Google Analytics:</strong> For website analytics and performance monitoring
                      <br />
                      <a href="https://policies.google.com/privacy" className="text-blue-600 hover:text-blue-800 text-sm">
                        Google Privacy Policy ↗
                      </a>
                    </div>
                  </li>
                  <li className="flex items-start">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-3 mt-2 flex-shrink-0" />
                    <div>
                      <strong>Content Delivery Networks (CDNs):</strong> For faster content delivery
                    </div>
                  </li>
                  <li className="flex items-start">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-3 mt-2 flex-shrink-0" />
                    <div>
                      <strong>Social Media Plugins:</strong> For social sharing functionality (when enabled)
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Updates to Policy */}
        <section className="mb-12">
          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Updates to this policy</h2>
            <p className="text-gray-700 mb-4">
              We may update this cookie policy from time to time to reflect changes in our practices 
              or applicable laws. When we make changes, we will update the "Last updated" date at 
              the bottom of this page and notify you through our website or email.
            </p>
            <p className="text-gray-700">
              We encourage you to review this policy periodically to stay informed about how we 
              use cookies and protect your privacy.
            </p>
          </div>
        </section>

        {/* Contact Information */}
        <section className="mb-12">
          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Questions or concerns?</h2>
            <p className="text-gray-700 mb-6">
              If you have any questions about this cookie policy or our privacy practices, 
              please don't hesitate to contact us:
            </p>
            
            <div className="grid sm:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Email</h3>
                <a href="mailto:privacy@gradvy.com" className="text-blue-600 hover:text-blue-800">
                  privacy@gradvy.com
                </a>
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Related Policies</h3>
                <div className="space-y-2">
                  <a href="/privacy-policy" className="block text-blue-600 hover:text-blue-800">
                    Privacy Policy
                  </a>
                  <a href="/terms-of-service" className="block text-blue-600 hover:text-blue-800">
                    Terms of Service
                  </a>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Last Updated */}
        <div className="text-center py-8">
          <p className="text-sm text-gray-500">
            Last updated: {new Date().toLocaleDateString('en-US', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </p>
        </div>
      </div>
    </div>
  );
};

export default CookiePolicyPage;