"use client";

import { useEffect } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import Script from "next/script";

interface GoogleAnalyticsProps {
  GA_MEASUREMENT_ID: string;
}

export default function GoogleAnalytics({
  GA_MEASUREMENT_ID,
}: GoogleAnalyticsProps) {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    const url = pathname + searchParams.toString();
    window.gtag("config", GA_MEASUREMENT_ID, {
      page_path: url,
    });
  }, [pathname, searchParams, GA_MEASUREMENT_ID]);

  return (
    <>
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`}
        strategy="afterInteractive"
      />
      <Script id="google-analytics" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', '${GA_MEASUREMENT_ID}');
        `}
      </Script>
    </>
  );
}
