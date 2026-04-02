import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "BIZIT | Universal Marketplace",
  description: "One Protocol, Infinite Markets.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
