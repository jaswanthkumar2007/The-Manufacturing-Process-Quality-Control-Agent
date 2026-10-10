/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        factory: {
          900: "#0a0a1a",
          800: "#12122a",
          700: "#1a1a3e",
          600: "#22224e",
          500: "#2e2e6e",
        },
        accent: {
          blue:   "#3b82f6",
          cyan:   "#06b6d4",
          green:  "#10b981",
          yellow: "#f59e0b",
          red:    "#ef4444",
          purple: "#8b5cf6",
        },
      },
      fontFamily: {
        mono:  ["'JetBrains Mono'", "monospace"],
        sans:  ["'Inter'", "sans-serif"],
      },
      animation: {
        "pulse-slow":  "pulse 3s cubic-bezier(0.4,0,0.6,1) infinite",
        "slide-in":    "slideIn 0.3s ease-out",
        "glow":        "glow 2s ease-in-out infinite",
      },
      keyframes: {
        slideIn: {
          "0%":   { opacity: "0", transform: "translateY(-8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        glow: {
          "0%, 100%": { boxShadow: "0 0 5px rgba(59,130,246,0.4)" },
          "50%":      { boxShadow: "0 0 20px rgba(59,130,246,0.8)" },
        },
      },
      backgroundImage: {
        "grid-pattern": "linear-gradient(rgba(59,130,246,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(59,130,246,0.05) 1px, transparent 1px)",
      },
      backgroundSize: {
        "grid-sm": "20px 20px",
      },
    },
  },
  plugins: [],
};
