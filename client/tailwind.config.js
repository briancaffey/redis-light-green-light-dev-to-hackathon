/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./App.vue",
  ],
  theme: {
    extend: {
      fontFamily: {
        heading: ["Komikax", 'sans-serif'],
        body: ["Komikax", 'sans-serif']
      }
    },
  },
  plugins: [],
}