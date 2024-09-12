import React from "react";
import { Metadata } from "next";
import "./globals.css";

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
    <html data-theme="mytheme" lang="en">
      <body className="font-main">
        <header className="bg-primary text-white font-main h-12 flex justify-left items-center pl-3">
          Class Schedule Generator
        </header>
        {children}
        {/* <footer className="bg-secondary text-white font-main h-12 flex justify-left items-center pl-3">
          Created by: Brennan Humphrey
        </footer> */}
      </body>
    </html>
  );
}
