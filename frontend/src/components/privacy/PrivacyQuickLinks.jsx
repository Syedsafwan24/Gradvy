'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { useToast } from '@/hooks/useToast';

export default function PrivacyQuickLinks() {
  const { toast } = useToast();

  const openCookiePreferences = () => {
    const event = new CustomEvent('openCookiePreferences', { bubbles: true });
    window.dispatchEvent(event);
  };

  const downloadConsentHistory = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/preferences/consent-history/download/', {
        method: 'GET',
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to download');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'consent-history.json';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast({ title: 'Download started', description: 'Consent history downloading.' });
    } catch (e) {
      toast({ title: 'Download failed', description: 'Could not download consent history.', variant: 'destructive' });
    }
  };

  const revokeAllConsents = async () => {
    if (!confirm('Revoke all non-essential consents? This limits personalization and analytics.')) return;
    try {
      const res = await fetch('http://localhost:8000/api/preferences/consent/revoke-all/', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!res.ok) throw new Error('Failed');
      toast({ title: 'Consents revoked', description: 'All non-essential consents withdrawn.' });
    } catch (e) {
      toast({ title: 'Action failed', description: 'Could not revoke consents.', variant: 'destructive' });
    }
  };

  return (
    <Card className="p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Privacy Quick Links</h2>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <Button onClick={openCookiePreferences} className="justify-start">Manage Cookie Preferences</Button>
        <Button onClick={downloadConsentHistory} variant="outline" className="justify-start">Download Consent History</Button>
        <Button onClick={revokeAllConsents} variant="destructive" className="justify-start">Revoke All Consents</Button>
        <Link href="/privacy-policy" className="inline-flex">
          <Button variant="ghost" className="justify-start w-full">View Privacy Policy</Button>
        </Link>
        <Link href="/cookie-policy" className="inline-flex">
          <Button variant="ghost" className="justify-start w-full">View Cookie Policy</Button>
        </Link>
        <Link href="/terms" className="inline-flex">
          <Button variant="ghost" className="justify-start w-full">View Terms of Service</Button>
        </Link>
      </div>
    </Card>
  );
}

