import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { Toaster } from 'react-hot-toast';
import './globals.css';

const inter = Inter({ 
  subsets: ['latin', 'cyrillic'],
  variable: '--font-sans',
});

export const metadata: Metadata = {
  title: 'ChatFlow - Professional Real-time Chat',
  description: 'Modern, secure, and feature-rich chat application',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uz" className="dark">
      <body className={`${inter.variable} font-sans antialiased`}>
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#1e293b',
              color: '#f1f5f9',
              border: '1px solid rgba(100, 116, 139, 0.2)',
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#f1f5f9',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#f1f5f9',
              },
            },
          }}
        />
      </body>
    </html>
  );
}
