'use client'

import Link from 'next/link'
import AuthStatus from '@/components/AuthStatus'

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-harvey-dark flex flex-col">
      {/* Navigation */}
      <nav className="bg-harvey-dark border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <Link href="/" className="flex items-center gap-4">
              <h1 className="text-2xl font-serif-heading text-white">LawScout AI</h1>
            </Link>
            <AuthStatus />
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 w-full">
        <div className="mb-8">
          <Link
            href="/"
            className="text-gray-400 hover:text-white transition-colors text-sm font-light inline-flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Home
          </Link>
        </div>

        <div className="prose prose-invert max-w-none">
          <h1 className="text-4xl md:text-5xl font-serif-heading text-white mb-6">
            Privacy Policy
          </h1>
          
          <p className="text-gray-400 text-sm mb-8 font-light">
            Last Updated: December 19, 2025
          </p>

          <div className="text-gray-300 font-light leading-relaxed space-y-8">
            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">1. Introduction</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                LawScout AI ("we," "our," or "us") is committed to protecting your privacy. 
                This Privacy Policy explains how we collect, use, disclose, and safeguard 
                your information when you use our legal research platform at lawscoutai.com 
                (the "Service").
              </p>
              <p className="text-gray-300 leading-relaxed">
                By using our Service, you agree to the collection and use of information in 
                accordance with this policy. If you do not agree with our policies and practices, 
                please do not use our Service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">2. Information We Collect</h2>
              
              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">2.1 Personal Information</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                When you register for an account, we collect:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Email address</li>
                <li>Full name (optional)</li>
                <li>Password (encrypted)</li>
                <li>Account creation date</li>
              </ul>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">2.2 OAuth Information</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                If you sign in with Google, we receive:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Email address</li>
                <li>Full name</li>
                <li>Profile picture (not stored)</li>
                <li>Google user ID (for authentication only)</li>
              </ul>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">2.3 Usage Data</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                We automatically collect:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Search queries (to improve search accuracy)</li>
                <li>Search history and timestamps</li>
                <li>IP address and device information</li>
                <li>Browser type and version</li>
                <li>Pages visited and time spent</li>
                <li>Search count (for free tier limit enforcement)</li>
              </ul>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">2.4 Cookies and Tracking</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                We use cookies and similar technologies to:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Keep you signed in</li>
                <li>Remember your preferences</li>
                <li>Analyze usage patterns</li>
                <li>Improve our Service</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">3. How We Use Your Information</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                We use the collected information for:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li><strong className="text-white">Service Provision:</strong> To provide and maintain our legal research platform</li>
                <li><strong className="text-white">Authentication:</strong> To verify your identity and secure your account</li>
                <li><strong className="text-white">Search Limits:</strong> To track and enforce the 15 free searches per account</li>
                <li><strong className="text-white">Communication:</strong> To send service updates, security alerts, and support messages</li>
                <li><strong className="text-white">Improvement:</strong> To analyze usage and improve search accuracy</li>
                <li><strong className="text-white">Legal Compliance:</strong> To comply with legal obligations and prevent fraud</li>
                <li><strong className="text-white">Marketing:</strong> To send promotional emails (you can opt-out anytime)</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">4. Data Storage and Security</h2>
              
              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">4.1 Where We Store Data</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                Your data is stored on secure servers located in the United States. We use:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Encrypted databases (SQLite with encryption at rest)</li>
                <li>HTTPS/TLS for all data transmission</li>
                <li>Industry-standard security measures</li>
                <li>Regular security audits and updates</li>
              </ul>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">4.2 Data Retention</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                We retain your data:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li><strong className="text-white">Account data:</strong> Until you delete your account</li>
                <li><strong className="text-white">Search history:</strong> For 90 days, then anonymized</li>
                <li><strong className="text-white">Usage logs:</strong> For 30 days for security and debugging</li>
                <li><strong className="text-white">Payment data:</strong> As required by law (if applicable)</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">5. Data Sharing and Disclosure</h2>
              
              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">5.1 We DO NOT Sell Your Data</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                We do not sell, rent, or trade your personal information to third parties.
              </p>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">5.2 We May Share With:</h3>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li><strong className="text-white">Service Providers:</strong> Hosting providers, payment processors (when implemented), 
                analytics services (Google Analytics) - under strict confidentiality agreements</li>
                <li><strong className="text-white">Legal Requirements:</strong> When required by law, court order, or government request</li>
                <li><strong className="text-white">Business Transfers:</strong> In case of merger, acquisition, or sale of assets</li>
                <li><strong className="text-white">With Your Consent:</strong> When you explicitly authorize sharing</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">6. Your Privacy Rights</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                You have the right to:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li><strong className="text-white">Access:</strong> Request a copy of your personal data</li>
                <li><strong className="text-white">Correction:</strong> Update or correct inaccurate information</li>
                <li><strong className="text-white">Deletion:</strong> Request deletion of your account and data</li>
                <li><strong className="text-white">Export:</strong> Download your search history and data</li>
                <li><strong className="text-white">Opt-Out:</strong> Unsubscribe from marketing emails</li>
                <li><strong className="text-white">Object:</strong> Object to certain data processing activities</li>
              </ul>
              <p className="text-gray-300 leading-relaxed mb-4">
                To exercise these rights, contact us at{' '}
                <a href="mailto:support@lawscoutai.com" className="text-blue-400 hover:text-blue-300 hover:underline">
                  support@lawscoutai.com
                </a>
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">7. Children's Privacy</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                Our Service is not intended for children under 18 years of age. We do not 
                knowingly collect personal information from children. If you are a parent or 
                guardian and believe your child has provided us with personal information, 
                please contact us immediately.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">8. Third-Party Links</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                Our Service may contain links to external websites (case law sources, legal 
                databases). We are not responsible for the privacy practices of these third-party 
                sites. We encourage you to review their privacy policies.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">9. International Users</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                Our servers are located in the United States. If you access our Service from 
                outside the US, your data may be transferred to and processed in the US. By 
                using our Service, you consent to this transfer.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">10. Changes to This Policy</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                We may update this Privacy Policy from time to time. We will notify you of 
                material changes by:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Posting the new policy on this page</li>
                <li>Updating the "Last Updated" date</li>
                <li>Sending an email notification (for significant changes)</li>
              </ul>
              <p className="text-gray-300 leading-relaxed">
                Your continued use of the Service after changes constitutes acceptance of the 
                updated policy.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">11. Contact Us</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                If you have questions about this Privacy Policy, please contact us:
              </p>
              <div className="bg-gray-900/50 border border-gray-800 p-4 rounded-lg">
                <p className="text-gray-300 mb-2 font-light">
                  <strong className="text-white">Email:</strong>{' '}
                  <a href="mailto:support@lawscoutai.com" className="text-blue-400 hover:text-blue-300 hover:underline">
                    support@lawscoutai.com
                  </a>
                </p>
                <p className="text-gray-300 font-light">
                  <strong className="text-white">Website:</strong>{' '}
                  <a href="https://lawscoutai.com" className="text-blue-400 hover:text-blue-300 hover:underline">
                    lawscoutai.com
                  </a>
                </p>
              </div>
            </section>

            <section className="bg-blue-950/30 border-l-4 border-blue-500 p-6 rounded-r-lg">
              <h3 className="text-lg font-serif-heading text-blue-300 mb-2">Your Privacy Matters</h3>
              <p className="text-blue-200 font-light">
                We are committed to transparency and protecting your privacy. This policy 
                reflects our dedication to responsible data handling. If you have concerns, 
                please reach out - we're here to help.
              </p>
            </section>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-20 bg-harvey-dark">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex justify-center space-x-8 text-sm text-gray-500">
            <Link href="/support" className="hover:text-white transition-colors font-light">Support</Link>
            <Link href="/terms" className="hover:text-white transition-colors font-light">Terms</Link>
            <Link href="/privacy" className="hover:text-white transition-colors font-light">Privacy</Link>
            <a href="https://www.courtlistener.com/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors font-light">
              US Courts & Case Law
            </a>
          </div>
          <div className="mt-8 text-center text-sm text-gray-600 font-light">
            <p>Legal case opinions sourced from <a href="https://www.courtlistener.com/" target="_blank" rel="noopener noreferrer" className="text-white hover:underline">CourtListener</a>, a project of the <a href="https://free.law/" target="_blank" rel="noopener noreferrer" className="text-white hover:underline">Free Law Project</a>.</p>
            <p className="mt-2">Contract data from the <a href="https://www.atticusprojectai.org/cuad" target="_blank" rel="noopener noreferrer" className="text-white hover:underline">CUAD Dataset</a>.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
