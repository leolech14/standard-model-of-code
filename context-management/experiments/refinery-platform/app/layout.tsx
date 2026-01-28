import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Cloud Context Refinery",
  description: "Multi-tenant context processing platform (L7→L8 spinoff)",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-neutral-950 text-neutral-200">
        {children}
      </body>
    </html>
  );
}
