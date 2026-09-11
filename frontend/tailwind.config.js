/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          50: '#f0f7ff',
          100: '#e0effe',
          500: '#0052cc',
          700: '#003b99',
          800: '#072c66',
          900: '#061d43',
        },
        watershed: {
          blue: '#1976d2',
          green: '#2e7d32',
          amber: '#f57c00',
          red: '#d32f2f',
          surface: '#0f172a',
        }
      },
    },
  },
  plugins: [],
};
