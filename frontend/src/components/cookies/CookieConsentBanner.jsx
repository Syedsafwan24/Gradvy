/**
 * Cookie Consent Banner Component
 * Displays a banner for cookie consent management
 */

import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { Button } from '../ui/Button';
import { CookieBanner, isCookieConsentSet } from '@/lib/cookieUtils';

const CookieConsentBanner = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    // Check if consent banner should be shown
    const shouldShow = !isCookieConsentSet();
    
    if (shouldShow) {
      // Delay showing banner for better UX
      const timer = setTimeout(() => {
        setIsVisible(true);
        setIsAnimating(true);
      }, 1500);
      
      return () => clearTimeout(timer);
    }

    // Listen for custom events to show/hide banner
    const handleShowBanner = (event) => {
      if (event.detail.show) {
        setIsVisible(true);
        setTimeout(() => setIsAnimating(true), 100);
      } else {
        setIsAnimating(false);
        setTimeout(() => setIsVisible(false), 300);
      }
    };

    window.addEventListener('showCookieBanner', handleShowBanner);
    return () => window.removeEventListener('showCookieBanner', handleShowBanner);
  }, []);

  const handleAcceptAll = () => {
    setIsAnimating(false);
    setTimeout(() => {
      CookieBanner.acceptAll();
      setIsVisible(false);
    }, 300);
  };

  const handleAcceptEssential = () => {
    setIsAnimating(false);
    setTimeout(() => {
      CookieBanner.acceptEssential();
      setIsVisible(false);
    }, 300);
  };

  const handleOpenPreferences = () => {
    CookieBanner.openPreferences();
  };

  const handleClose = () => {
    setIsAnimating(false);
    setTimeout(() => {
      setIsVisible(false);
    }, 300);
  };

  if (!isVisible) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className={`fixed inset-0 bg-black/20 backdrop-blur-sm z-40 transition-opacity duration-300 ${
          isAnimating ? 'opacity-100' : 'opacity-0'
        }`}
        onClick={handleClose}
      />
      
      {/* Banner */}
      <div 
        className={`fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-2xl transform transition-transform duration-300 ease-in-out ${
          isAnimating ? 'translate-y-0' : 'translate-y-full'
        }`}
      >
        <div className="max-w-7xl mx-auto p-6">
          {/* Close button */}
          <button
            onClick={handleClose}
            className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close cookie banner"
          >
            <X size={20} />
          </button>

          <div className="pr-12">
            {/* Banner content */}
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                🍪 We value your privacy
              </h3>
              <p className="text-gray-700 text-sm leading-relaxed max-w-4xl">
                We use cookies and similar technologies to enhance your browsing experience, 
                personalize content, analyze traffic, and improve our services. Some cookies 
                are essential for the site to function, while others help us understand how 
                you interact with our platform to provide you with a better experience.
              </p>
            </div>

            {/* Cookie categories preview */}
            <div className="mb-6 flex flex-wrap gap-2">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                ✓ Essential (Always Active)
              </span>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                Analytics
              </span>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                Functional
              </span>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                Marketing
              </span>
            </div>

            {/* Action buttons */}
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
              <Button
                onClick={handleAcceptAll}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 text-sm font-medium transition-colors"
              >
                Accept All Cookies
              </Button>
              
              <Button
                onClick={handleAcceptEssential}
                variant="outline"
                className="border-gray-300 text-gray-700 hover:bg-gray-50 px-6 py-2.5 text-sm font-medium transition-colors"
              >
                Essential Only
              </Button>
              
              <Button
                onClick={handleOpenPreferences}
                variant="ghost"
                className="text-gray-600 hover:text-gray-800 px-6 py-2.5 text-sm font-medium transition-colors"
              >
                Customize Preferences
              </Button>
            </div>

            {/* Policy links */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                By clicking "Accept All Cookies", you agree to our{' '}
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
                . You can change your preferences at any time in your account settings.
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default CookieConsentBanner;