import './globals.css';
import type { Metadata } from 'next';
import { Inter, Crimson_Text } from 'next/font/google';
import { ThemeProvider } from '@/components/theme-provider';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';
import { ChatWithArticle } from '@/components/chat-with-article';
import { Toaster } from '@/components/ui/sonner';

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-sans',
});

const crimsonText = Crimson_Text({
  subsets: ['latin'],
  weight: ['400', '600', '700'],
  variable: '--font-serif',
});

export const metadata: Metadata = {
  title: 'FuseNews - Decentralized News Platform',
  description: 'A blockchain-powered news platform with AI-driven recommendations and anonymous publishing.',
  keywords: ['news', 'blockchain', 'decentralized', 'AI', 'journalism'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${crimsonText.variable} font-sans antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem={false}
          disableTransitionOnChange
        >
          <div className="min-h-screen flex flex-col">
            <Navbar />
            <main className="flex-1">
              {children}
            </main>
            <Footer />
          </div>
          <ChatWithArticle />
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}