import type { Metadata } from "next";
import { Geist, Geist_Mono, Manrope, Oswald } from "next/font/google";
import "./globals.css";
import { ClickSound } from "@/components/ClickSound";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
});

const oswald = Oswald({
  variable: "--font-oswald",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Yokalma, La carte de fidélité qui ne se perd jamais",
  description:
    "Yokalma remplace les cartes de fidélité papier par une carte digitale dans Google Wallet. Créez votre programme, partagez-le par WhatsApp ou QR Code, et faites revenir vos clients. Pensé pour les commerces de proximité en Afrique de l'Ouest.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="fr"
      className={`${geistSans.variable} ${geistMono.variable} ${manrope.variable} ${oswald.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-sans">
        {children}
        <ClickSound />
      </body>
    </html>
  );
}
