'use client';

import React from 'react';
import Link from 'next/link';

export default function CookiesAliasPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold mb-4">Cookie Policy</h1>
      <p className="mb-4">This page redirects to our full cookie policy.</p>
      <Link href="/cookie-policy" className="text-blue-600 underline">
        View Cookie Policy
      </Link>
    </div>
  );
}

