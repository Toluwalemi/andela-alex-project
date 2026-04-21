"use client";

import Link from "next/link";
import { SignedIn, SignedOut, SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";

export function Navigation() {
  return (
    <header className="nav">
      <div>
        <Link href="/" className="wordmark">
          Alex
        </Link>
        <div className="tagline">Portfolio and retirement review</div>
      </div>
      <div className="nav-links">
        <Link href="/dashboard">Dashboard</Link>
        <Link href="/portfolio">Portfolio</Link>
        <Link href="/analysis">Analysis</Link>
        <Link href="/history">History</Link>
        <SignedOut>
          <SignInButton mode="modal">
            <button className="secondary" type="button">
              Sign in
            </button>
          </SignInButton>
          <SignUpButton mode="modal">
            <button type="button">Get started</button>
          </SignUpButton>
        </SignedOut>
        <SignedIn>
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
      </div>
    </header>
  );
}
