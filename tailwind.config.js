/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./src/**/*.{html,js,svelte,ts}"],
  safelist: ["dark"],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border) / <alpha-value>)",
        input: "hsl(var(--input) / <alpha-value>)",
        ring: "hsl(var(--ring) / <alpha-value>)",
        background: "hsl(var(--background) / <alpha-value>)",
        foreground: "hsl(var(--foreground) / <alpha-value>)",
        primary: {
          DEFAULT: "hsl(var(--primary) / <alpha-value>)",
          foreground: "hsl(var(--primary-foreground) / <alpha-value>)",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary) / <alpha-value>)",
          foreground: "hsl(var(--secondary-foreground) / <alpha-value>)",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive) / <alpha-value>)",
          foreground: "hsl(var(--destructive-foreground) / <alpha-value>)",
        },
        muted: {
          DEFAULT: "hsl(var(--muted) / <alpha-value>)",
          foreground: "hsl(var(--muted-foreground) / <alpha-value>)",
        },
        accent: {
          DEFAULT: "hsl(var(--accent) / <alpha-value>)",
          foreground: "hsl(var(--accent-foreground) / <alpha-value>)",
        },
        popover: {
          DEFAULT: "hsl(var(--popover) / <alpha-value>)",
          foreground: "hsl(var(--popover-foreground) / <alpha-value>)",
        },
        card: {
          DEFAULT: "hsl(var(--card) / <alpha-value>)",
          foreground: "hsl(var(--card-foreground) / <alpha-value>)",
        },
        // Custom fintech colors
        emerald: {
          DEFAULT: "#10B981",
          glow: "rgba(16, 185, 129, 0.4)",
        },
        rose: {
          DEFAULT: "#F43F5E",
          glow: "rgba(244, 63, 94, 0.4)",
        },
        amber: {
          DEFAULT: "#F59E0B",
          glow: "rgba(245, 158, 11, 0.4)",
        },
        navy: {
          DEFAULT: "#0F172A",
          light: "#1E293B",
          lighter: "#334155",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      backdropBlur: {
        glass: "12px",
      },
      animation: {
        "pulse-glow": "pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow-emerald": "glow-emerald 2s ease-in-out infinite alternate",
        "glow-rose": "glow-rose 2s ease-in-out infinite alternate",
        "glow-amber": "glow-amber 2s ease-in-out infinite alternate",
        "slide-up": "slide-up 0.3s ease-out",
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": { opacity: "1", boxShadow: "0 0 5px currentColor" },
          "50%": { opacity: "0.7", boxShadow: "0 0 20px currentColor" },
        },
        "glow-emerald": {
          "0%": { boxShadow: "0 0 2px #10B981" },
          "100%": { boxShadow: "0 0 8px #10B981, 0 0 16px rgba(16, 185, 129, 0.3)" },
        },
        "glow-rose": {
          "0%": { boxShadow: "0 0 2px #F43F5E" },
          "100%": { boxShadow: "0 0 8px #F43F5E, 0 0 16px rgba(244, 63, 94, 0.3)" },
        },
        "glow-amber": {
          "0%": { boxShadow: "0 0 2px #F59E0B" },
          "100%": { boxShadow: "0 0 8px #F59E0B, 0 0 16px rgba(245, 158, 11, 0.3)" },
        },
        "slide-up": {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
