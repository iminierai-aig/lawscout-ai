import type { Metadata } from 'next'
import Link from 'next/link'
import Script from 'next/script'
import './globals.css'
import { AuthProvider } from '@/contexts/AuthContext'

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://lawscoutai.com'),
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
          <div className="bg-blue-600 text-white text-center py-2 text-sm">
            🚀 Beta Testing Phase - Your feedback shapes our product! 
            <Link href="/support" className="underline ml-2">Report Issues</Link>
          </div>
          
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
