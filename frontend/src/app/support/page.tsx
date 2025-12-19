'use client'

import { useState } from 'react'
import Link from 'next/link'
import AuthStatus from '@/components/AuthStatus'
import { useAuth } from '@/contexts/AuthContext'

export default function SupportPage() {
  const { user, token } = useAuth()
  const [formData, setFormData] = useState({
    name: user?.full_name || '',
    email: user?.email || '',
    subject: '',
    message: '',
    category: 'general'
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError('')

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.lawscoutai.com'
      const response = await fetch(`${apiUrl}/api/support`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({
          ...formData,
          user_id: user?.id,
          url: window.location.href,
          user_agent: navigator.userAgent,
          timestamp: new Date().toISOString()
        })
      })

      if (!response.ok) throw new Error('Failed to submit')

      setSubmitted(true)
      
      setTimeout(() => {
        setSubmitted(false)
        setFormData({
          name: user?.full_name || '',
          email: user?.email || '',
          subject: '',
          message: '',
          category: 'general'
        })
      }, 3000)

    } catch (err) {
      setError('Failed to submit. Please email support@lawscoutai.com directly.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

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
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 w-full">
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

        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-serif-heading text-white mb-4">
            How can we help you?
          </h1>
          <p className="text-xl text-gray-400 font-light">
            Get support for your LawScout AI account
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Quick Help Cards */}
          <div className="md:col-span-3 grid md:grid-cols-3 gap-6 mb-8">
            {/* FAQ */}
            <div className="bg-harvey-dark border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-colors">
              <div className="w-12 h-12 bg-blue-900/30 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-serif-heading text-white mb-2">
                Frequently Asked Questions
              </h3>
              <p className="text-gray-400 text-sm mb-4 font-light">
                Find answers to common questions about using LawScout AI
              </p>
              <a href="#faq" className="text-blue-400 hover:text-blue-300 text-sm font-light transition-colors">
                View FAQs →
              </a>
            </div>

            {/* Email Support */}
            <div className="bg-harvey-dark border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-colors">
              <div className="w-12 h-12 bg-green-900/30 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-serif-heading text-white mb-2">
                Email Support
              </h3>
              <p className="text-gray-400 text-sm mb-4 font-light">
                Get help via email. We typically respond within 24 hours.
              </p>
              <a 
                href="mailto:support@lawscoutai.com" 
                className="text-blue-400 hover:text-blue-300 text-sm font-light transition-colors"
              >
                support@lawscoutai.com →
              </a>
            </div>

            {/* Help Center */}
            <div className="bg-harvey-dark border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-colors">
              <div className="w-12 h-12 bg-purple-900/30 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="text-lg font-serif-heading text-white mb-2">
                Getting Started Guide
              </h3>
              <p className="text-gray-400 text-sm mb-4 font-light">
                Learn how to use LawScout AI effectively
              </p>
              <a href="/help" className="text-blue-400 hover:text-blue-300 text-sm font-light transition-colors">
                View Guide →
              </a>
            </div>
          </div>

          {/* Contact Form */}
          <div className="md:col-span-2">
            <div className="bg-harvey-dark border border-gray-800 rounded-lg p-8">
              <h2 className="text-2xl font-serif-heading text-white mb-6">
                Contact Support
              </h2>

              {submitted ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-serif-heading text-white mb-2">
                    Message Sent!
                  </h3>
                  <p className="text-gray-400 font-light">
                    We've received your message and will respond within 24 hours.
                  </p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  {error && (
                    <div className="bg-red-950/50 border border-red-900 rounded-md p-4">
                      <p className="text-sm text-red-300">{error}</p>
                    </div>
                  )}

                  {/* Category */}
                  <div>
                    <label htmlFor="category" className="block text-sm font-light text-gray-400 mb-2">
                      What can we help you with?
                    </label>
                    <select
                      id="category"
                      name="category"
                      value={formData.category}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-700 bg-harvey-dark text-white rounded-md focus:ring-2 focus:ring-white focus:border-transparent"
                      required
                    >
                      <option value="general">General Question</option>
                      <option value="technical">Technical Issue</option>
                      <option value="billing">Billing Question</option>
                      <option value="feature">Feature Request</option>
                      <option value="bug">Bug Report</option>
                      <option value="account">Account Issue</option>
                      <option value="feedback">Feedback</option>
                    </select>
                  </div>

                  {/* Name */}
                  <div>
                    <label htmlFor="name" className="block text-sm font-light text-gray-400 mb-2">
                      Your Name
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-700 bg-harvey-dark text-white rounded-md focus:ring-2 focus:ring-white focus:border-transparent"
                      required
                    />
                  </div>

                  {/* Email */}
                  <div>
                    <label htmlFor="email" className="block text-sm font-light text-gray-400 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-700 bg-harvey-dark text-white rounded-md focus:ring-2 focus:ring-white focus:border-transparent"
                      required
                    />
                  </div>

                  {/* Subject */}
                  <div>
                    <label htmlFor="subject" className="block text-sm font-light text-gray-400 mb-2">
                      Subject
                    </label>
                    <input
                      type="text"
                      id="subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      placeholder="Brief description of your issue"
                      className="w-full px-4 py-2 border border-gray-700 bg-harvey-dark text-white placeholder-gray-600 rounded-md focus:ring-2 focus:ring-white focus:border-transparent"
                      required
                    />
                  </div>

                  {/* Message */}
                  <div>
                    <label htmlFor="message" className="block text-sm font-light text-gray-400 mb-2">
                      Message
                    </label>
                    <textarea
                      id="message"
                      name="message"
                      value={formData.message}
                      onChange={handleChange}
                      rows={6}
                      placeholder="Please provide as much detail as possible..."
                      className="w-full px-4 py-2 border border-gray-700 bg-harvey-dark text-white placeholder-gray-600 rounded-md focus:ring-2 focus:ring-white focus:border-transparent resize-none"
                      required
                    />
                    <p className="mt-2 text-sm text-gray-500 font-light">
                      Include relevant details like error messages, steps to reproduce, etc.
                    </p>
                  </div>

                  {/* Submit Button */}
                  <div>
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full bg-white text-harvey-dark py-3 px-6 rounded-md font-medium hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-harvey-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {isSubmitting ? 'Sending...' : 'Send Message'}
                    </button>
                  </div>

                  <p className="text-sm text-gray-500 text-center font-light">
                    Or email us directly at{' '}
                    <a href="mailto:support@lawscoutai.com" className="text-blue-400 hover:text-blue-300 hover:underline">
                      support@lawscoutai.com
                    </a>
                  </p>
                </form>
              )}
            </div>
          </div>

          {/* Sidebar - Response Time & Tips */}
          <div className="space-y-6">
            {/* Response Time */}
            <div className="bg-blue-950/30 border border-blue-900/50 rounded-lg p-6">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="w-6 h-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-serif-heading text-blue-300 mb-1">
                    Response Time
                  </h3>
                  <p className="text-sm text-blue-400/80 font-light">
                    We typically respond within <strong className="text-blue-300">24 hours</strong> during business days. 
                    Pro users get priority support.
                  </p>
                </div>
              </div>
            </div>

            {/* Tips for Better Support */}
            <div className="bg-harvey-dark border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-serif-heading text-white mb-4">
                💡 Tips for Better Support
              </h3>
              <ul className="space-y-3 text-sm text-gray-300 font-light">
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>Include error messages or screenshots</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>Describe steps to reproduce the issue</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>Mention your browser and device</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>Be as specific as possible</span>
                </li>
              </ul>
            </div>

            {/* Status */}
            <div className="bg-harvey-dark border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-serif-heading text-white mb-4">
                🟢 System Status
              </h3>
              <div className="space-y-2 text-sm font-light">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">API</span>
                  <span className="text-green-400 font-medium">Operational</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Search</span>
                  <span className="text-green-400 font-medium">Operational</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Authentication</span>
                  <span className="text-green-400 font-medium">Operational</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div id="faq" className="mt-16">
          <h2 className="text-3xl font-serif-heading text-white mb-8 text-center">
            Frequently Asked Questions
          </h2>

          <div className="max-w-3xl mx-auto space-y-4">
            {/* FAQ Items */}
            {[
              {
                q: "How many free searches do I get?",
                a: "Every account gets 15 free searches. After that, you'll need to upgrade to Pro for unlimited searches at $29/month."
              },
              {
                q: "What happens when I reach my search limit?",
                a: "Once you've used all 15 free searches, you'll be prompted to upgrade to Pro. Your account remains active, but you won't be able to perform new searches until you upgrade."
              },
              {
                q: "Can I reset my free searches?",
                a: "No, the 15 free searches are a one-time allotment per account. However, you can upgrade to Pro for unlimited searches."
              },
              {
                q: "How accurate are the search results?",
                a: "Our AI searches through 276,970+ legal documents using advanced vector search. While we strive for accuracy, always verify information with primary sources and consult qualified attorneys."
              },
              {
                q: "Is this legal advice?",
                a: "No. LawScout AI is a research tool, not a substitute for professional legal advice. Always consult qualified attorneys for legal matters."
              },
              {
                q: "Can I export search results?",
                a: "Export capabilities will be available for Pro users when the Pro tier launches."
              },
              {
                q: "How do I delete my account?",
                a: "Go to Dashboard → Account Settings → Delete Account. Note that this action is permanent and cannot be undone."
              },
              {
                q: "Do you offer refunds?",
                a: "When Pro tier launches, we'll offer a 30-day money-back guarantee for new subscribers."
              },
              {
                q: "Can I use this for commercial purposes?",
                a: "Yes, both Free and Pro tiers can be used for commercial legal research. However, you must comply with our Terms of Service."
              },
              {
                q: "How do I report a bug?",
                a: "Use the feedback button (bottom-right corner) or submit a support ticket above with category 'Bug Report'."
              }
            ].map((faq, index) => (
              <details
                key={index}
                className="bg-harvey-dark border border-gray-800 rounded-lg p-6 group hover:border-gray-700 transition-colors"
              >
                <summary className="font-serif-heading text-white cursor-pointer flex justify-between items-center">
                  <span>{faq.q}</span>
                  <svg 
                    className="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </summary>
                <p className="mt-4 text-gray-300 leading-relaxed font-light">
                  {faq.a}
                </p>
              </details>
            ))}
          </div>

          <div className="text-center mt-8">
            <p className="text-gray-400 font-light">
              Still have questions?{' '}
              <a href="mailto:support@lawscoutai.com" className="text-blue-400 hover:text-blue-300 hover:underline font-light">
                Contact our support team
              </a>
            </p>
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
