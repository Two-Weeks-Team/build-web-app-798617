import type { Metadata } from "next";
import { Libre_Baskerville, Manrope } from "next/font/google";
import "@/app/globals.css";

const serif = Libre_Baskerville({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-serif"
});

const sans = Manrope({
  subsets: ["latin"],
  weight: ["400", "500", "700", "800"],
  variable: "--font-sans"
});

export const metadata: Metadata = {
  title: "Build Web App — Product Planning Workbench",
  description: "Turn rough product ideas into traceable, reusable planning briefs in minutes."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${serif.variable} ${sans.variable} bg-background text-foreground`}>{children}</body>
    </html>
  );
}
