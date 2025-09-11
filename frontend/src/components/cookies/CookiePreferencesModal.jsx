/**
 * Cookie Preferences Modal Component
 * Allows users to customize their cookie preferences in detail
 */

import { useState, useEffect } from 'react';
import { X, Info, Shield, BarChart3, Zap, Target } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { 
  getCookiePreferences, 
  setCookiePreferences, 
  setCookieConsent,
  COOKIE_TYPES,
  COOKIE_POLICY_DATA
} from '@/lib/cookieUtils';

const CookiePreferencesModal = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [preferences, setPreferences] = useState({});
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    // Load current preferences
    const currentPrefs = getCookiePreferences();
    setPreferences(currentPrefs);

    // Listen for modal open events
    const handleOpenPreferences = () => {
      setIsOpen(true);
      // Reload preferences when modal opens
      const freshPrefs = getCookiePreferences();
      setPreferences(freshPrefs);
      setHasChanges(false);
    };

    window.addEventListener('openCookiePreferences', handleOpenPreferences);
    return () => window.removeEventListener('openCookiePreferences', handleOpenPreferences);
  }, []);

  const handlePreferenceChange = (cookieType, enabled) => {
    if (cookieType === COOKIE_TYPES.ESSENTIAL) return; // Cannot disable essential cookies
    
    const newPreferences = {
      ...preferences,
      [cookieType]: enabled
    };
    setPreferences(newPreferences);
    setHasChanges(true);
  };

  const handleSavePreferences = () => {
    setCookiePreferences(preferences);
    setCookieConsent(true);
    setHasChanges(false);
    setIsOpen(false);
  };

  const handleAcceptAll = () => {
    const allAccepted = Object.keys(COOKIE_TYPES).reduce((acc, type) => {
      acc[COOKIE_TYPES[type]] = true;
      return acc;
    }, {});
    
    setPreferences(allAccepted);
    setCookiePreferences(allAccepted);
    setCookieConsent(true);
    setHasChanges(false);
    setIsOpen(false);
  };

  const handleRejectAll = () => {
    const onlyEssential = {
      [COOKIE_TYPES.ESSENTIAL]: true,
      [COOKIE_TYPES.ANALYTICS]: false,
      [COOKIE_TYPES.MARKETING]: false,
      [COOKIE_TYPES.FUNCTIONAL]: false
    };
    
    setPreferences(onlyEssential);
    setCookiePreferences(onlyEssential);
    setCookieConsent(true);
    setHasChanges(false);
    setIsOpen(false);
  };

  const getCookieIcon = (type) => {
    switch (type) {
      case COOKIE_TYPES.ESSENTIAL:
        return <Shield className="w-5 h-5 text-green-600" />;
      case COOKIE_TYPES.ANALYTICS:
        return <BarChart3 className="w-5 h-5 text-blue-600" />;
      case COOKIE_TYPES.FUNCTIONAL:
        return <Zap className="w-5 h-5 text-purple-600" />;
      case COOKIE_TYPES.MARKETING:
        return <Target className="w-5 h-5 text-orange-600" />;
      default:
        return <Info className="w-5 h-5 text-gray-600" />;
    }
  };

  const getCookieTypeColor = (type) => {
    switch (type) {
      case COOKIE_TYPES.ESSENTIAL:
        return 'text-green-600';
      case COOKIE_TYPES.ANALYTICS:
        return 'text-blue-600';
      case COOKIE_TYPES.FUNCTIONAL:
        return 'text-purple-600';
      case COOKIE_TYPES.MARKETING:
        return 'text-orange-600';
      default:
        return 'text-gray-600';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
        onClick={() => setIsOpen(false)}
      />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div 
          className="relative bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  🍪 Cookie Preferences
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Customize your cookie settings to control how we collect and use information
                </p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X size={24} />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-4 overflow-y-auto max-h-[60vh]">
            <div className="space-y-6">
              {Object.entries(COOKIE_POLICY_DATA).map(([cookieType, data]) => {
                const isEnabled = preferences[cookieType];
                const isEssential = cookieType === COOKIE_TYPES.ESSENTIAL;
                
                return (
                  <div key={cookieType} className="border border-gray-200 rounded-lg p-4">
                    {/* Cookie type header */}
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getCookieIcon(cookieType)}
                        <h3 className={`font-semibold ${getCookieTypeColor(cookieType)}`}>
                          {data.name}
                        </h3>
                        {isEssential && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Always Active
                          </span>
                        )}
                      </div>
                      
                      {/* Toggle switch */}
                      <div className="flex items-center">
                        <button
                          disabled={isEssential}
                          onClick={() => handlePreferenceChange(cookieType, !isEnabled)}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                            isEnabled
                              ? 'bg-blue-600'
                              : 'bg-gray-200'
                          } ${isEssential ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              isEnabled ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      </div>
                    </div>

                    {/* Description */}
                    <p className="text-sm text-gray-600 mb-3 leading-relaxed">
                      {data.description}
                    </p>

                    {/* Examples */}
                    <div className="mb-2">
                      <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                        Examples:
                      </h4>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {data.examples.map((example, index) => (
                          <li key={index} className="flex items-center">
                            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full mr-2 flex-shrink-0" />
                            {example}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Duration */}
                    <p className="text-xs text-gray-500">
                      <span className="font-medium">Duration:</span> {data.duration}
                    </p>
                  </div>
                );
              })}
            </div>

            {/* Additional info */}
            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-start space-x-2">
                <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-blue-800">
                  <p className="font-medium mb-1">Important Information:</p>
                  <ul className="space-y-1 text-blue-700">
                    <li>• Essential cookies cannot be disabled as they are required for basic site functionality</li>
                    <li>• Your preferences will be saved and applied across all pages</li>
                    <li>• You can change these settings at any time from your account settings</li>
                    <li>• Some features may not work properly if certain cookies are disabled</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
            <div className="flex flex-col sm:flex-row gap-3 sm:justify-between sm:items-center">
              <div className="flex gap-3">
                <Button
                  onClick={handleAcceptAll}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2"
                >
                  Accept All
                </Button>
                <Button
                  onClick={handleRejectAll}
                  variant="outline"
                  className="border-gray-300 text-gray-700 hover:bg-gray-50 px-6 py-2"
                >
                  Reject All
                </Button>
              </div>
              
              <div className="flex gap-3">
                <Button
                  onClick={() => setIsOpen(false)}
                  variant="ghost"
                  className="text-gray-600 hover:text-gray-800 px-6 py-2"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleSavePreferences}
                  disabled={!hasChanges}
                  className={`px-6 py-2 ${
                    hasChanges
                      ? 'bg-green-600 hover:bg-green-700 text-white'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  Save Preferences
                </Button>
              </div>
            </div>
            
            <div className="mt-3 pt-3 border-t border-gray-200">
              <p className="text-xs text-gray-500 text-center">
                For more information, please read our{' '}
                <a 
                  href="/privacy-policy" 
                  className="text-blue-600 hover:text-blue-800 underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Privacy Policy
                </a>{' '}
                and{' '}
                <a 
                  href="/cookie-policy" 
                  className="text-blue-600 hover:text-blue-800 underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Cookie Policy
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CookiePreferencesModal;