/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        studio: {
          bg: '#0d0d12',
          surface: '#151520',
          card: '#1c1c2b',
          border: '#2a2a3d',
          accent: '#ffb36b',
          primary: '#6366f1',
          highlight: '#ffdf00',
        }
      },
      fontFamily: {
        vietnam: ['"Be Vietnam Pro"', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
