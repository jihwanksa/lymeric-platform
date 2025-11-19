import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import NavBar from "./components/NavBar";

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
        <Providers>
          <NavBar />
          {children}
        </Providers>
      </body>
    </html>
  );
}
