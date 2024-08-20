import type { Config } from "tailwindcss";


const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        main: ["Roboto"]
      }
    },
  },
  plugins: [
    require('daisyui')
  ],
  daisyui: {
    themes: ["light", "dark", {
      mytheme: {
        
"primary": "#991b1b",
        
"secondary": "#f97316",
        
"accent": "#f3f4f6",
        
"neutral": "#f3f4f6",
        
"base-100": "#f3f4f6",
        
"info": "#f3f4f6",
        
"success": "#f3f4f6",
        
"warning": "#111827",
        
"error": "#111827",
        },
      },]
  },
  
};

export default config;
