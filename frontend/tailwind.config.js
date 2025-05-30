/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx}", // pages folder
    "./src/components/**/*.{js,ts,jsx,tsx}", // components folder
  ],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
};
