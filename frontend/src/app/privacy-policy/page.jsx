'use client';

import React from 'react';
import Link from 'next/link';
import { Card } from '@/components/ui/Card';

export default function PrivacyPolicyPage() {
  const version = '1.0.0';
  const effectiveDate = '2025-01-01';

  const toc = [
    { id: 'overview', label: '1. Overview' },
    { id: 'data-we-collect', label: '2. Data We Collect' },
    { id: 'how-we-use', label: '3. How We Use Data' },
    { id: 'legal-bases', label: '4. Legal Bases' },
    { id: 'cookies', label: '5. Cookies & Preferences' },
    { id: 'sharing', label: '6. Sharing & Processors' },
    { id: 'retention', label: '7. Retention & Deletion' },
    { id: 'your-rights', label: '8. Your Rights' },
    { id: 'security', label: '9. Security' },
    { id: 'transfers', label: '10. International Transfers' },
    { id: 'children', label: '11. Children’s Privacy' },
    { id: 'changes', label: '12. Changes to This Policy' },
    { id: 'contact', label: '13. Contact' },
  ];

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight">Privacy Policy</h1>
        <p className="text-sm text-gray-500 mt-2">Version {version} • Effective {effectiveDate}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* TOC */}
        <aside className="lg:col-span-4 xl:col-span-3">
          <Card className="p-5 sticky top-4">
            <h2 className="text-base font-semibold mb-3">Contents</h2>
            <nav className="space-y-2">
              {toc.map((item) => (
                <a key={item.id} href={`#${item.id}`} className="block text-sm text-gray-700 hover:text-blue-600">
                  {item.label}
                </a>
              ))}
            </nav>
          </Card>
        </aside>

        {/* Content */}
        <section className="lg:col-span-8 xl:col-span-9">
          <Card className="p-6">
            <div className="prose prose-gray max-w-none">
              <h2 id="overview">1. Overview</h2>
              <p>
                This Privacy Policy explains how Gradvy collects, uses, shares, and protects your
                information. We apply data minimization, consent-based processing, and privacy-by-design.
              </p>

              <h2 id="data-we-collect">2. Data We Collect</h2>
              <ul>
                <li>
                  <strong>Account & Authentication:</strong> name, email, credentials, session/device metadata.
                </li>
                <li>
                  <strong>Learning Preferences & Activity:</strong> onboarding answers, content preferences,
                  interactions (e.g., course views, quiz attempts), and analytics events (if consented).
                </li>
                <li>
                  <strong>Recommendations & Insights:</strong> AI-generated insights and cached recommendations
                  based on your activity (if consented).
                </li>
                <li>
                  <strong>Cookies & Similar Technologies:</strong> essential, analytics, functional, and marketing
                  cookies depending on your preferences.
                </li>
                <li>
                  <strong>Optional Social/Profile Data:</strong> if you connect accounts (e.g., LinkedIn, GitHub),
                  we import permitted data for enrichment (subject to your consent and provider terms).
                </li>
              </ul>

              <h2 id="how-we-use">3. How We Use Data</h2>
              <ul>
                <li>Provide and maintain the service and your account</li>
                <li>Personalize content and recommendations (with consent)</li>
                <li>Measure performance and improve features (with consent)</li>
                <li>Detect abuse, secure the platform, and comply with law</li>
              </ul>

              <h2 id="legal-bases">4. Legal Bases</h2>
              <p>Depending on your location and the processing purpose, we rely on:</p>
              <ul>
                <li><strong>Consent</strong> (e.g., analytics, personalization, marketing)</li>
                <li><strong>Contract</strong> (to provide core services you request)</li>
                <li><strong>Legitimate interests</strong> (e.g., security, service improvement)</li>
                <li><strong>Legal obligations</strong> (where required by law)</li>
              </ul>

              <h2 id="cookies">5. Cookies & Preferences</h2>
              <p>
                Manage cookie categories from the Cookie Preferences modal or the Privacy Settings page.
                Essential cookies are required; analytics, functional, and marketing are optional.
                See our <Link href="/cookie-policy" className="text-blue-600">Cookie Policy</Link> for details.
              </p>
              <ul>
                <li><strong>Essential:</strong> auth session, CSRF, consent state</li>
                <li><strong>Functional:</strong> UI and preference enhancements</li>
                <li><strong>Analytics:</strong> usage and performance metrics</li>
                <li><strong>Marketing:</strong> optional communications and ads</li>
              </ul>

              <h2 id="sharing">6. Sharing & Processors</h2>
              <p>
                We do not sell personal data. We may share with service providers acting on our behalf
                (e.g., analytics, email, infrastructure) under data processing agreements. Examples may
                include analytics platforms or email providers. Specific processors can change; we evaluate
                privacy and security before onboarding.
              </p>

              <h2 id="retention">7. Retention & Deletion</h2>
              <p>
                We retain data only as long as necessary for the purposes described. You can revoke non-essential
                consents at any time. Interactions and training data may be subject to retention windows and
                periodic cleanup. You may request deletion of your account and data.
              </p>

              <h2 id="your-rights">8. Your Rights</h2>
              <ul>
                <li><strong>Access & Export:</strong> request a copy of your data</li>
                <li><strong>Rectification:</strong> correct inaccurate information</li>
                <li><strong>Erasure:</strong> request deletion of personal data</li>
                <li><strong>Restriction & Objection:</strong> limit processing or object to certain uses</li>
                <li><strong>Withdraw Consent:</strong> at any time for non-essential processing</li>
              </ul>
              <p>
                You can manage consents in-app (Settings → Privacy). For export/erasure requests, contact us at
                <a href="mailto:privacy@gradvy.com" className="text-blue-600"> privacy@gradvy.com</a>.
              </p>

              <h2 id="security">9. Security</h2>
              <p>
                We apply layered security measures including transport encryption, access controls, and monitoring.
                No system is perfectly secure; we encourage strong passwords and MFA.
              </p>

              <h2 id="transfers">10. International Transfers</h2>
              <p>
                If data is transferred across borders, we use appropriate safeguards (e.g., standard contractual
                clauses) where required by applicable law.
              </p>

              <h2 id="children">11. Children’s Privacy</h2>
              <p>
                The service is not directed to children under the age of 13 (or older, per local law). We do not
                knowingly collect data from children without appropriate consent.
              </p>

              <h2 id="changes">12. Changes to This Policy</h2>
              <p>
                We may update this policy from time to time. Material changes will be highlighted in the app.
                Your continued use after the Effective Date indicates acceptance.
              </p>

              <h2 id="contact">13. Contact</h2>
              <p>
                Email: <a href="mailto:privacy@gradvy.com" className="text-blue-600">privacy@gradvy.com</a>
              </p>
            </div>
          </Card>
        </section>
      </div>
    </div>
  );
}
