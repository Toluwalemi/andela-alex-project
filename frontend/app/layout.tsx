import type { Metadata } from "next";
import type { ReactNode } from "react";
import { ClerkProvider } from "@clerk/nextjs";

import "./globals.css";
import { Navigation } from "@/components/navigation";

const clerkPublishableKey =
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ?? "pk_test_Y2xlcmsuZXhhbXBsZS5jb20k";

export const metadata: Metadata = {
  title: "Alex",
  description: "Financial planning advisor SaaS"
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <ClerkProvider publishableKey={clerkPublishableKey}>
      <html lang="en">
        <body>
          <div className="shell">
            <Navigation />
            <main>{children}</main>
          </div>
        </body>
      </html>
    </ClerkProvider>
  );
}
