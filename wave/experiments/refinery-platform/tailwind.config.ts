import type { Config } from "tailwindcss";

export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  // Colors now defined via OKLCH tokens in globals.css @theme directive.
  // No color overrides needed here.
  plugins: [],
} satisfies Config;
