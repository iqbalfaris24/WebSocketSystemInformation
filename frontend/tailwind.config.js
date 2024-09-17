/** @type {import('tailwindcss').Config} */
export default {
 content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode:"class",
  theme: {
    extend: {
      backgroundColor: {
        'navy-blue': '#002F5D',
        'dark-blue': '#014475',
      },
      // textColor: {
      //   'custom-red': '#E53E3E',
      // }
    },
  },
  // plugins: [require('daisyui')],
  
}

