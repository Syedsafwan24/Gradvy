'use client';

import React from 'react';
import { Card } from '@/components/ui/Card';

export default function TermsPage() {
  const version = '1.0.0';
  const effectiveDate = '2025-01-01';

  const toc = [
    { id: 'acceptance', label: '1. Acceptance of Terms' },
    { id: 'eligibility', label: '2. Eligibility & Accounts' },
    { id: 'use', label: '3. Use of the Service' },
    { id: 'user-content', label: '4. User Content & License' },
    { id: 'ip', label: '5. Intellectual Property' },
    { id: 'subscriptions', label: '6. Subscriptions & Payments' },
    { id: 'third-parties', label: '7. Third-Party Services' },
    { id: 'termination', label: '8. Termination' },
    { id: 'disclaimers', label: '9. Disclaimers' },
    { id: 'liability', label: '10. Limitation of Liability' },
    { id: 'indemnity', label: '11. Indemnification' },
    { id: 'governing-law', label: '12. Governing Law' },
    { id: 'disputes', label: '13. Dispute Resolution' },
    { id: 'changes', label: '14. Changes to Terms' },
    { id: 'contact', label: '15. Contact' },
  ];

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight">Terms of Service</h1>
        <p className="text-sm text-gray-500 mt-2">Version {version} • Effective {effectiveDate}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
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

        <section className="lg:col-span-8 xl:col-span-9">
          <Card className="p-6">
            <div className="prose prose-gray max-w-none">
              <h2 id="acceptance">1. Acceptance of Terms</h2>
              <p>
                By accessing or using Gradvy, you agree to be bound by these Terms. If you do not agree,
                you may not use the Service.
              </p>

              <h2 id="eligibility">2. Eligibility & Accounts</h2>
              <ul>
                <li>You must be of legal age to form a binding contract in your jurisdiction.</li>
                <li>You are responsible for maintaining the confidentiality of your account and credentials.</li>
                <li>You must provide accurate information and keep it up to date.</li>
              </ul>

              <h2 id="use">3. Use of the Service</h2>
              <p>When using the Service, you agree not to:</p>
              <ul>
                <li>Violate any applicable laws or regulations</li>
                <li>Interfere with or disrupt the Service or its infrastructure</li>
                <li>Reverse engineer, decompile, or attempt to access source code</li>
                <li>Upload malicious code or engage in abusive behavior</li>
              </ul>

              <h2 id="user-content">4. User Content & License</h2>
              <p>
                You retain ownership of content you submit to the Service. You grant Gradvy a worldwide,
                non-exclusive, transferable, sublicensable license to host, store, display, and process
                your content solely to operate and improve the Service.
              </p>

              <h2 id="ip">5. Intellectual Property</h2>
              <p>
                The Service, including software, interfaces, and branding, is owned by Gradvy and its
                licensors and is protected by intellectual property laws. No rights are granted except as
                expressly stated in these Terms.
              </p>

              <h2 id="subscriptions">6. Subscriptions & Payments</h2>
              <p>
                If paid plans are offered, pricing, billing cycles, taxes, and refund policies will be
                disclosed at purchase. Where applicable, subscriptions renew automatically unless cancelled
                in accordance with the plan terms.
              </p>

              <h2 id="third-parties">7. Third-Party Services</h2>
              <p>
                The Service may integrate with or link to third-party services. We are not responsible for
                those services or their terms and policies. Your use of third-party services is at your own
                risk and subject to their terms.
              </p>

              <h2 id="termination">8. Termination</h2>
              <p>
                We may suspend or terminate access to the Service for any violation of these Terms or if
                required by law. You may stop using the Service at any time.
              </p>

              <h2 id="disclaimers">9. Disclaimers</h2>
              <p>
                THE SERVICE IS PROVIDED “AS IS” AND “AS AVAILABLE” WITHOUT WARRANTIES OF ANY KIND, EXPRESS
                OR IMPLIED. WE DISCLAIM ALL WARRANTIES TO THE MAXIMUM EXTENT PERMITTED BY LAW.
              </p>

              <h2 id="liability">10. Limitation of Liability</h2>
              <p>
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, GRADVY AND ITS AFFILIATES SHALL NOT BE LIABLE FOR
                INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS,
                REVENUE, DATA, OR USE.
              </p>

              <h2 id="indemnity">11. Indemnification</h2>
              <p>
                You agree to indemnify and hold Gradvy harmless from any claims arising from your use of the
                Service or violation of these Terms.
              </p>

              <h2 id="governing-law">12. Governing Law</h2>
              <p>
                These Terms are governed by the laws of the applicable jurisdiction where Gradvy operates,
                without regard to conflict of laws principles.
              </p>

              <h2 id="disputes">13. Dispute Resolution</h2>
              <p>
                Before resorting to formal dispute resolution, please contact us to attempt an informal
                resolution. Additional dispute resolution terms may apply based on your location.
              </p>

              <h2 id="changes">14. Changes to Terms</h2>
              <p>
                We may update these Terms from time to time. Material changes will be communicated in the app.
                Your continued use after the Effective Date constitutes acceptance.
              </p>

              <h2 id="contact">15. Contact</h2>
              <p>Email: support@gradvy.com</p>
            </div>
          </Card>
        </section>
      </div>
    </div>
  );
}
