import type { Config } from "tailwindcss";

export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // Match reference design colors
      colors: {
        primary: {
          DEFAULT: '#10b981', // emerald-500
          dark: '#059669',
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
