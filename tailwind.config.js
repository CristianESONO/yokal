/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
      },
      colors: {
        primary: {
          DEFAULT: '#3B82F6',
          hover: '#2563EB',
          text: '#ffffff',
        },
        fidup: {
          500: '#3B82F6',
          600: '#2563EB',
        },
      },
    },
  },
  plugins: [],
};
