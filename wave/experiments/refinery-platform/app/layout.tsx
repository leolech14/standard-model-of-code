import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { ThemeProvider } from "@/components/layout/ThemeProvider";
import { ToastProvider } from "@/components/ui/Toast";
import RainmakerCloud from "@/components/widgets/RainmakerCloud";

export const metadata: Metadata = {
  title: "Cloud Context Refinery",
  description: "Multi-tenant context processing platform (L7 to L8 spinoff)",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <ToastProvider>
            <div className="flex h-screen">
              <Sidebar />
              <main className="flex-1 overflow-auto">
                {children}
              </main>
            </div>
            <RainmakerCloud />
          </ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
