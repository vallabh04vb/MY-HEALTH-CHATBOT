import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'UHC Insurance Policy Chatbot',
  description: 'AI-powered chatbot for UnitedHealthcare insurance policy queries',
  keywords: ['insurance', 'UHC', 'healthcare', 'chatbot', 'AI', 'medical billing'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
