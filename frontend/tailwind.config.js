/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        },
        risk: {
          prohibited: '#ef4444',
          high: '#f97316',
          limited: '#eab308',
          minimal: '#22c55e',
        }
      }
    },
  },
  plugins: [],
}
