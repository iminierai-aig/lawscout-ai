import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'LawScout AI - Legal Research',
  description: 'AI-powered legal research platform with hybrid search',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
