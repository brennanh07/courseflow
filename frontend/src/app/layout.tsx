import React from "react";
import { Metadata } from "next";
import "./globals.css";
import SmartClassSchedulerButton from "./NavButton";
import { GoogleAnalytics } from '@next/third-parties/google'

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
        <div className="navbar bg-base-100">
          <div className="flex-none"></div>
          <div className="flex-1">
            <SmartClassSchedulerButton />
          </div>
        </div>
        {children}
      </body>
      <GoogleAnalytics gaId="G-DX4DXYGB7K" />
    </html>
  );
}
