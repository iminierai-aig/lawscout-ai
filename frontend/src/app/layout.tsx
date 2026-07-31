import type { Metadata } from 'next'
import Link from 'next/link'
import Script from 'next/script'
import './globals.css'
import { AuthProvider } from '@/contexts/AuthContext'

export const metadata: Metadata = {
  metadataBase: new URL('https://lawscoutai.com'),
  title: 'LawScout AI - AI-Powered Legal Research',
  description: 'Master legal concepts and procedures, draft precise documents, and conduct thorough analysis. Free legal research powered by AI.',
  keywords: 'legal research, AI legal assistant, case law, legal documents, legal analysis',
  authors: [{ name: 'LawScout AI' }],
  openGraph: {
    title: 'LawScout AI - AI-Powered Legal Research',
    description: 'Master legal concepts and procedures with AI-powered legal research.',
    url: 'https://lawscoutai.com',
    siteName: 'LawScout AI',
    images: ['/og-image.png'], // You'll need to add this
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'LawScout AI',
    description: 'AI-Powered Legal Research Platform',
    images: ['/og-image.png'],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&display=swap" rel="stylesheet" />
      </head>
      <body>
        {process.env.NEXT_PUBLIC_GA_ID && (
          <>
            <Script src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`} strategy="afterInteractive" />
            <Script id="google-analytics" strategy="afterInteractive">
              {`window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}');`}
            </Script>
          </>
        )}
        <AuthProvider>
          {/* Beta Banner */}
          <div className="bg-blue-600 text-white text-center py-2 text-sm relative z-10">
            🚀 Beta Testing Phase - Your feedback shapes our product!
            <Link href="/support" className="underline ml-2 hover:text-blue-100">Report Issues</Link>
          </div>

          {/* Sticky Info Banner */}
          <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border-b border-blue-500/30 py-2.5 sticky top-0 z-40 backdrop-blur-sm">
            <div className="max-w-7xl mx-auto px-4">
              <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
                <div className="flex flex-wrap items-center gap-4 md:gap-6">
                  <span className="text-gray-300">
                    <span className="font-bold text-blue-400">276,970+</span> legal docs
                  </span>
                  <span className="text-gray-300">
                    <span className="font-bold text-blue-400">15</span> free searches
                  </span>
                  <span className="text-gray-300">
                    <span className="font-bold text-blue-400">$29/mo</span> Pro
                  </span>
                </div>
                <Link
                  href="/support"
                  className="text-blue-300 hover:text-white font-bold whitespace-nowrap transition border border-blue-400/30 px-3 py-1 rounded-lg hover:border-blue-400 hover:bg-blue-500/20"
                >
                  Examples & FAQ →
                </Link>
              </div>
            </div>
          </div>

          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
