import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Lymeric Data Platform",
  description: "Chemistry-aware data management for materials research",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <nav className="border-b bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-blue-600">Lymeric Data Platform</h1>
              </div>
              <div className="flex space-x-8">
                <a href="/" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">
                  Dashboard
                </a>
                <a href="/materials" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">Materials
                </a>
                <a href="/upload" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">
                  Upload
                </a>
                <a href="/predictions" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">
                  Predictions
                </a>
              </div>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
