import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#070A12",
          panel: "#0E121C",
          panelHi: "#161B28",
          deep: "#040610",
        },
        ink: {
          50: "#FBFDFF",
          100: "#E6F1FF",
          200: "#C8D3E6",
          300: "#A3B0C7",
          400: "#8A93A8",
          500: "#6E7689",
          600: "#5A6378",
          700: "#3F4658",
          800: "#1F2533",
          900: "#0E121C",
          950: "#070A12",
        },
        mint: {
          DEFAULT: "#6EE7B7",
          dim: "#34D399",
          deep: "#059669",
        },
        amber: {
          DEFAULT: "#FBBF24",
          dim: "#D97706",
        },
        violet: {
          DEFAULT: "#A78BFA",
          dim: "#7C3AED",
        },
        rose: {
          DEFAULT: "#F472B6",
          dim: "#DB2777",
        },
        accent: {
          DEFAULT: "#6EE7B7",
          dim: "#34D399",
        },
      },
      fontFamily: {
        sans: ["var(--font-geist)", "ui-sans-serif", "system-ui", "-apple-system", "sans-serif"],
        mono: ["var(--font-jetbrains)", "ui-monospace", "Menlo", "monospace"],
      },
      boxShadow: {
        panel:
          "inset 0 1px 0 rgba(255,255,255,0.04), 0 12px 32px -12px rgba(0,0,0,0.6)",
        glow:
          "0 0 0 1px rgba(110,231,183,0.2), 0 0 32px -4px rgba(110,231,183,0.25)",
        "glow-mint": "0 0 24px -4px rgba(110,231,183,0.45)",
        "glow-amber": "0 0 24px -4px rgba(251,191,36,0.45)",
      },
      backgroundImage: {
        "panel-gradient":
          "linear-gradient(180deg, #161B28 0%, #0E121C 100%)",
        "page-radial":
          "radial-gradient(ellipse at top, #0E1322 0%, #070A12 60%)",
      },
      keyframes: {
        pulse_dot: {
          "0%, 100%": { opacity: "1", transform: "scale(1)" },
          "50%": { opacity: "0.5", transform: "scale(0.85)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        "pulse-dot": "pulse_dot 2.4s ease-in-out infinite",
        shimmer: "shimmer 2.4s linear infinite",
      },
    },
  },
  plugins: [],
};

export default config;
