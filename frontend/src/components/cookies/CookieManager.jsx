/**
 * Cookie Manager Component
 * Main component that handles all cookie-related functionality
 * Includes banner, preferences modal, and initialization
 */

import { useEffect } from 'react';
import CookieConsentBanner from './CookieConsentBanner';
import CookiePreferencesModal from './CookiePreferencesModal';
import { initializeCookieManagement } from '@/lib/cookieUtils';

const CookieManager = () => {
  useEffect(() => {
    // Initialize cookie management on component mount
    initializeCookieManagement();
  }, []);

  return (
    <>
      <CookieConsentBanner />
      <CookiePreferencesModal />
    </>
  );
};

export default CookieManager;