/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}", // чтобы Tailwind видел все компоненты
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}