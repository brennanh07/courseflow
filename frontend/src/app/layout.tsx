import React from "react";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: {
    absolute: "",
    default: "Class Schedule Generator",
    template: "%s | Class Schedule Generator",
  },
  description: "Program to generate optimal class schedules",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header
          style={{
            color: "white",
            backgroundColor: "maroon",
            padding: "1rem",
          }}
        >
          Header
        </header>
        {children}
        <footer
          style={{
            color: "white",
            backgroundColor: "darkorange",
            padding: "1rem",
          }}
        >
          Footer
        </footer>
      </body>
    </html>
  );
}
