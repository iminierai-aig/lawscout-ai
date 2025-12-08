/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        'serif-heading': ['Playfair Display', 'Georgia', 'Times New Roman', 'serif'],
      },
      colors: {
        'harvey-dark': '#1a1a1a',
        'harvey-light': '#f5f5f5',
      },
    },
  },
  plugins: [],
}
