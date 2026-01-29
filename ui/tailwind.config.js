/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0f172a",
        panel: "#111827",
        card: "rgba(255,255,255,0.05)",
        accent: "#7c3aed",
      },
      backdropBlur: {
        xl: "20px",
      }
    },
  },
  plugins: [],
}
