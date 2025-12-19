'use client'

import Link from 'next/link'
import AuthStatus from '@/components/AuthStatus'

export default function TermsPage() {
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
            Terms of Service
          </h1>
          
          <p className="text-gray-400 text-sm mb-8 font-light">
            Last Updated: December 19, 2025
          </p>

          <div className="text-gray-300 font-light leading-relaxed space-y-8">
            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">1. Agreement to Terms</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                By accessing or using LawScout AI ("Service," "Platform," "we," "us," or "our") 
                at lawscoutai.com, you agree to be bound by these Terms of Service ("Terms"). 
                If you disagree with any part of these terms, you may not access the Service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">2. Description of Service</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                LawScout AI is an AI-powered legal research platform that provides:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Access to a database of 276,970+ legal documents including cases, contracts, and opinions</li>
                <li>AI-powered search and analysis tools</li>
                <li>Legal research assistance and citation management</li>
                <li>Document analysis and summarization</li>
              </ul>
              
              <div className="bg-red-950/30 border-l-4 border-red-500 p-6 rounded-r-lg my-6">
                <h3 className="text-lg font-serif-heading text-red-300 mb-2">⚠️ Important Disclaimer</h3>
                <p className="text-red-200 mb-2">
                  <strong>THIS IS NOT LEGAL ADVICE.</strong> LawScout AI is a research tool only. 
                  The Service does not provide legal advice, does not create an attorney-client 
                  relationship, and is not a substitute for professional legal counsel.
                </p>
                <p className="text-red-200">
                  Always verify information with primary sources and consult qualified attorneys 
                  for legal matters affecting you.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">3. User Accounts</h2>
              
              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">3.1 Registration</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                To use certain features, you must register for an account. You agree to:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Provide accurate, current, and complete information</li>
                <li>Maintain and update your information</li>
                <li>Keep your password secure and confidential</li>
                <li>Notify us immediately of unauthorized access</li>
                <li>Be responsible for all activities under your account</li>
              </ul>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">3.2 Eligibility</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                You must be at least 18 years old to use the Service. By using the Service, 
                you represent that you meet this requirement.
              </p>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">3.3 Account Termination</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                We reserve the right to suspend or terminate your account if:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>You violate these Terms</li>
                <li>You engage in fraudulent or abusive behavior</li>
                <li>You use the Service for illegal purposes</li>
                <li>Your account remains inactive for 12 months</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">4. Service Plans and Pricing</h2>
              
              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">4.1 Free Tier</h3>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>15 searches per account (lifetime limit)</li>
                <li>Full access to legal database</li>
                <li>AI-powered search capabilities</li>
                <li>No credit card required</li>
              </ul>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">4.2 Pro Tier (Coming Soon)</h3>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Unlimited searches</li>
                <li>Priority support</li>
                <li>Advanced AI features</li>
                <li>Export capabilities</li>
                <li>API access</li>
                <li>Price: $29/month (subject to change)</li>
              </ul>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">4.3 Payment Terms</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                When Pro tier launches:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Subscriptions are billed monthly in advance</li>
                <li>All fees are non-refundable except as required by law</li>
                <li>We may change pricing with 30 days notice</li>
                <li>Cancellation takes effect at the end of the current billing period</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">5. Acceptable Use Policy</h2>
              
              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">5.1 You MAY:</h3>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Use the Service for legal research purposes</li>
                <li>Search for cases, contracts, and legal opinions</li>
                <li>Analyze legal documents</li>
                <li>Export results (Pro tier, when available)</li>
              </ul>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">5.2 You MAY NOT:</h3>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Scrape, crawl, or use automated tools to access the Service</li>
                <li>Circumvent search limits or security measures</li>
                <li>Share your account credentials with others</li>
                <li>Resell or redistribute our content</li>
                <li>Use the Service for illegal purposes</li>
                <li>Attempt to hack, disrupt, or overload our systems</li>
                <li>Upload malicious code or viruses</li>
                <li>Impersonate others or misrepresent affiliation</li>
                <li>Violate any applicable laws or regulations</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">6. Intellectual Property</h2>
              
              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">6.1 Our Content</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                The Service, including software, algorithms, design, text, graphics, and 
                compilation of legal documents, is owned by LawScout AI or its licensors. 
                Protected by copyright, trademark, and other intellectual property laws.
              </p>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">6.2 Legal Documents</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                Legal documents (cases, contracts, opinions) in our database are public domain 
                or used under license. Citations and references to original sources are provided.
              </p>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">6.3 Your Content</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                You retain ownership of any content you submit (feedback, queries). By submitting 
                content, you grant us a license to use it to improve the Service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">7. Disclaimers and Limitations</h2>
              
              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">7.1 No Legal Advice</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                THE SERVICE DOES NOT PROVIDE LEGAL ADVICE. All information is for research 
                purposes only. We do not review content for accuracy or completeness. You 
                must independently verify all information.
              </p>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">7.2 "As Is" Service</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY 
                KIND, EXPRESS OR IMPLIED. We do not guarantee:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Accuracy, completeness, or timeliness of information</li>
                <li>Uninterrupted or error-free operation</li>
                <li>That defects will be corrected</li>
                <li>Freedom from viruses or harmful components</li>
              </ul>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">7.3 Limitation of Liability</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, LAWSCOUT AI SHALL NOT BE LIABLE FOR:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Indirect, incidental, or consequential damages</li>
                <li>Loss of profits, data, or business opportunities</li>
                <li>Damages resulting from use or inability to use the Service</li>
                <li>Reliance on information provided by the Service</li>
              </ul>
              <p className="text-gray-300 leading-relaxed mb-4">
                OUR TOTAL LIABILITY SHALL NOT EXCEED THE AMOUNT YOU PAID US IN THE PAST 12 MONTHS, 
                OR $100, WHICHEVER IS GREATER.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">8. Indemnification</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                You agree to indemnify and hold harmless LawScout AI from any claims, damages, 
                or expenses (including attorney fees) arising from:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Your use or misuse of the Service</li>
                <li>Your violation of these Terms</li>
                <li>Your violation of any rights of others</li>
                <li>Your violation of applicable laws</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">9. Termination</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                Either party may terminate this agreement at any time:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li><strong>You:</strong> Delete your account from account settings</li>
                <li><strong>Us:</strong> Suspend or terminate accounts that violate Terms</li>
              </ul>
              <p className="text-gray-300 leading-relaxed mb-4">
                Upon termination:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Your right to use the Service immediately ends</li>
                <li>We may delete your account and data (subject to legal requirements)</li>
                <li>Sections 6, 7, 8, 10, and 11 survive termination</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">10. Dispute Resolution</h2>
              
              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">10.1 Governing Law</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                These Terms are governed by the laws of Florida/USA, without regard 
                to conflict of law principles.
              </p>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">10.2 Informal Resolution</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                Before filing a claim, please contact{' '}
                <a href="mailto:support@lawscoutai.com" className="text-blue-400 hover:text-blue-300 hover:underline">
                  support@lawscoutai.com
                </a>{' '}
                to resolve the dispute informally.
              </p>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">10.3 Arbitration</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                If informal resolution fails, disputes will be resolved through binding 
                arbitration in accordance with [Arbitration Association] rules, except:
              </p>
              <ul className="list-disc pl-6 text-gray-300 space-y-2 mb-4">
                <li>Small claims court actions (under $10,000)</li>
                <li>Intellectual property disputes</li>
                <li>Injunctive or equitable relief</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">11. General Provisions</h2>
              
              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">11.1 Modifications</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                We may modify these Terms at any time. Material changes will be notified via 
                email or in-app notification. Continued use after changes constitutes acceptance.
              </p>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">11.2 Severability</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                If any provision is found invalid, the remaining provisions remain in effect.
              </p>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">11.3 Entire Agreement</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                These Terms, together with our Privacy Policy, constitute the entire agreement 
                between you and LawScout AI.
              </p>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">11.4 Assignment</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                You may not assign or transfer these Terms. We may assign our rights and 
                obligations without restriction.
              </p>

              <h3 className="text-xl font-serif-heading text-gray-200 mb-3">11.5 Waiver</h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                Our failure to enforce any right or provision does not constitute a waiver.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-serif-heading text-white mb-4">12. Contact Information</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                Questions about these Terms? Contact us:
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
              <h3 className="text-lg font-serif-heading text-blue-300 mb-2">By Using LawScout AI</h3>
              <p className="text-blue-200 mb-3 font-light">
                You acknowledge that you have read, understood, and agree to be bound by these Terms of Service.
              </p>
              <p className="text-blue-200 text-sm font-light">
                Last Updated: December 19, 2025
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
