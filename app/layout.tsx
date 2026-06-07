import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Inter, Caveat } from "next/font/google";
import { Toaster } from "sonner";
import { StoreProvider } from "@/store/provider";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const caveat = Caveat({
  variable: "--font-caveat",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "HandwritOCR — Handwriting Synthesis",
  description:
    "Transform typed text into realistic handwriting. Upload your handwriting samples and generate beautiful handwritten documents.",
  keywords: [
    "handwriting",
    "synthesis",
    "AI",
    "handwritten",
    "text",
    "PDF",
    "generator",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`dark ${geistSans.variable} ${geistMono.variable} ${inter.variable} ${caveat.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-sans">
        <StoreProvider>
          {children}
          <Toaster
            position="bottom-right"
            toastOptions={{
              style: {
                background: "rgba(20, 20, 20, 0.9)",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                color: "rgba(255, 255, 255, 0.9)",
                backdropFilter: "blur(12px)",
              },
            }}
          />
        </StoreProvider>
      </body>
    </html>
  );
}
